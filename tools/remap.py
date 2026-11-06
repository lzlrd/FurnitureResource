"""Rebuild baked Bedrock furniture textures from other vanilla textures.

The Bedrock textures in resources/customModel were baked in Blockbench from
the Java models: every face is a (sometimes resampled) copy of part of a
vanilla texture such as oak_planks. build_mapping() works out which vanilla
pixel each baked pixel came from; render() then rebuilds the sheet with
replacement textures (spruce_planks, red_wool, ...).
"""

import json
from pathlib import Path
from typing import Callable

import numpy as np

FACES = ("north", "east", "south", "west", "up", "down")

TextureLoader = Callable[[str], np.ndarray]


def first_frame(array: np.ndarray) -> np.ndarray:
    # Animated textures are tall strips; keep the first square frame.
    return array[: array.shape[1]]


def orientations(array: np.ndarray):
    """Yield the eight dihedral transforms of a 2D array."""
    for flip in (False, True):
        base = np.fliplr(array) if flip else array
        for turns in range(4):
            yield np.rot90(base, turns)


def resolve_texture(textures: dict, reference: str) -> str | None:
    seen = set()
    while reference and reference.startswith("#"):
        key = reference[1:]
        if key in seen:
            return None
        seen.add(key)
        reference = textures.get(key)
    if reference is None:
        return None
    return reference.split(":")[-1].removeprefix("block/")


def geo_cubes(geo: dict) -> list[dict]:
    cubes = []
    for bone in geo["minecraft:geometry"][0]["bones"]:
        cubes.extend(bone.get("cubes", []))
    return cubes


def pair_cubes(elements: list[dict], cubes: list[dict]) -> list[dict | None]:
    """Pair each Bedrock cube with its Java element by position and size.

    Blockbench mirrors X on Bedrock export: origin = (8 - to.x, from.y, from.z - 8).
    """
    expectations = []
    for element in elements:
        fx, fy, fz = element["from"]
        tx, ty, tz = element["to"]
        expectations.append(np.array([8 - tx, fy, fz - 8, tx - fx, ty - fy, tz - fz]))
    pairs = []
    for cube in cubes:
        actual = np.array([*cube["origin"], *cube["size"]])
        errors = [np.abs(actual - expected).sum() for expected in expectations]
        best = int(np.argmin(errors)) if errors else None
        pairs.append(elements[best] if best is not None and errors[best] < 0.05 else None)
    return pairs


def face_rect(uv: dict, width: int, height: int):
    (u, v), (w, h) = uv["uv"], uv["uv_size"]
    x0, x1 = sorted((u, u + w))
    y0, y1 = sorted((v, v + h))
    x0, y0 = max(int(np.floor(x0)), 0), max(int(np.floor(y0)), 0)
    x1, y1 = min(int(np.ceil(x1)), width), min(int(np.ceil(y1)), height)
    return x0, y0, x1, y1


def resample(source: np.ndarray, java_uv, rows: int, cols: int, offset: float):
    size = source.shape[0]
    scale = size / 16
    u1, v1, u2, v2 = (c * scale for c in java_uv)
    xs = np.floor(u1 + (np.arange(cols) + offset) * (u2 - u1) / cols).astype(int)
    ys = np.floor(v1 + (np.arange(rows) + offset) * (v2 - v1) / rows).astype(int)
    return np.clip(ys, 0, size - 1), np.clip(xs, 0, size - 1)


def match_resampled(region, index, source, java_uv):
    """Exact match of a straight resample of the Java UV, in any orientation."""
    for oriented, oriented_index in zip(orientations(region), orientations(index)):
        mask = oriented[..., 3] > 0
        rows, cols = oriented.shape[:2]
        for offset in (0.5, 0.0):
            ys, xs = resample(source, java_uv, rows, cols, offset)
            if np.array_equal(source[np.ix_(ys, xs)][mask], oriented[mask]):
                return ys, xs, oriented_index
    return None


def match_window(region, index, sources: dict, declared: str | None, hint):
    """Exact match of an unscaled (possibly wrapped) window of any source."""
    best = None
    for name, source in sources.items():
        size = source.shape[0]
        for orientation, (oriented, oriented_index) in enumerate(
            zip(orientations(region), orientations(index))
        ):
            mask = oriented[..., 3] > 0
            rows, cols = oriented.shape[:2]
            for sy in range(size):
                ys = (np.arange(rows) + sy) % size
                for sx in range(size):
                    xs = (np.arange(cols) + sx) % size
                    if np.array_equal(source[np.ix_(ys, xs)][mask], oriented[mask]):
                        score = (
                            0 if name == declared else 1,
                            0 if orientation == 0 else 1,
                            abs(sy - hint[0]) + abs(sx - hint[1]) if hint else 0,
                            orientation,
                        )
                        if best is None or score < best[0]:
                            best = (score, name, ys, xs, oriented_index)
    return best[1:] if best else None


def approximate(region, mask, index, source, java_uv, radius: int = 2):
    """Fallback for faces Blockbench baked with an irregular resample.

    Use the orientation whose straight resample agrees with the most pixels,
    then map each pixel to the nearest same-coloured source pixel within
    `radius` of where the resample puts it (or that position if none is).
    """
    best = None
    for oriented, oriented_index in zip(orientations(region), orientations(index)):
        rows, cols = oriented.shape[:2]
        oriented_mask = oriented[..., 3] > 0
        for offset in (0.5, 0.0):
            ys, xs = resample(source, java_uv, rows, cols, offset)
            agree = int((np.all(source[np.ix_(ys, xs)] == oriented, axis=-1) & oriented_mask).sum())
            if best is None or agree > best[0]:
                best = (agree, oriented, oriented_index, ys, xs)
    _, oriented, oriented_index, ys, xs = best
    size = source.shape[0]
    cols = region.shape[1]
    result = {}
    for a in range(oriented.shape[0]):
        for b in range(oriented.shape[1]):
            ry, rx = divmod(int(oriented_index[a, b]), cols)
            if not mask[ry, rx]:
                continue
            target = oriented[a, b]
            expected = (int(ys[a]), int(xs[b]))
            found = None
            for distance in range(radius + 1):
                for dy in range(-distance, distance + 1):
                    for dx in range(-distance, distance + 1):
                        if found or max(abs(dy), abs(dx)) != distance:
                            continue
                        sy, sx = expected[0] + dy, expected[1] + dx
                        if 0 <= sy < size and 0 <= sx < size and np.array_equal(source[sy, sx], target):
                            found = (sy, sx)
                if found:
                    break
            result[(ry, rx)] = found or expected
    return result


def build_mapping(model_dir: Path, model: str, atlas: np.ndarray, load: TextureLoader) -> dict:
    java = json.loads((model_dir / f"{model}.json").read_text())
    geo = json.loads((model_dir / f"{model}.geo.json").read_text())
    height, width = atlas.shape[:2]

    textures = java.get("textures", {})
    names = sorted({name for key in textures if (name := resolve_texture(textures, f"#{key}"))})
    sources = {name: first_frame(load(name)) for name in names}
    source_names = list(sources)

    cubes = geo_cubes(geo)
    pairs = pair_cubes(java.get("elements", []), cubes)

    # mapping[y, x] = (source index, source y, source x); -1 where unmapped.
    mapping = np.full((height, width, 3), -1, dtype=np.int32)

    def assign(x0, y0, region_shape, oriented_index, ys, xs, source_index, mask):
        cols = region_shape[1]
        for a in range(oriented_index.shape[0]):
            for b in range(oriented_index.shape[1]):
                ry, rx = divmod(int(oriented_index[a, b]), cols)
                if mask[ry, rx] and mapping[y0 + ry, x0 + rx, 0] == -1:
                    mapping[y0 + ry, x0 + rx] = (source_index, ys[a], xs[b])

    for cube, element in zip(cubes, pairs):
        for face in FACES:
            uv = cube.get("uv", {}).get(face)
            if not uv:
                continue
            x0, y0, x1, y1 = face_rect(uv, width, height)
            if x1 <= x0 or y1 <= y0:
                continue
            region = atlas[y0:y1, x0:x1]
            mask = region[..., 3] > 0
            if not mask.any():
                continue
            index = np.arange(region.shape[0] * region.shape[1]).reshape(region.shape[:2])

            java_face = (element or {}).get("faces", {}).get(face) or {}
            declared = resolve_texture(textures, java_face.get("texture", ""))
            java_uv = java_face.get("uv")
            hint = (min(java_uv[1], java_uv[3]), min(java_uv[0], java_uv[2])) if java_uv else None

            if java_uv and declared in sources:
                found = match_resampled(region, index, sources[declared], java_uv)
                if found:
                    ys, xs, oriented_index = found
                    assign(x0, y0, region.shape, oriented_index, ys, xs, source_names.index(declared), mask)
                    continue

            found = match_window(region, index, sources, declared, hint)
            if found:
                name, ys, xs, oriented_index = found
                assign(x0, y0, region.shape, oriented_index, ys, xs, source_names.index(name), mask)
                continue

            if java_uv and declared in sources:
                source_index = source_names.index(declared)
                for (ry, rx), (sy, sx) in approximate(region, mask, index, sources[declared], java_uv).items():
                    if mapping[y0 + ry, x0 + rx, 0] == -1:
                        mapping[y0 + ry, x0 + rx] = (source_index, sy, sx)

    opaque = atlas[..., 3] > 0
    return {
        "atlas": atlas,
        "mapping": mapping,
        "sources": source_names,
        "opaque": int(opaque.sum()),
        "mapped": int(((mapping[..., 0] >= 0) & opaque).sum()),
    }


def render(result: dict, load: TextureLoader, substitutions: dict[str, str]) -> np.ndarray:
    """Rebuild the sheet, swapping source textures per `substitutions`.

    Pixels that did not come from a vanilla texture are kept as they are.
    """
    out = result["atlas"].copy()
    mapping = result["mapping"]
    for source_index, name in enumerate(result["sources"]):
        texture = first_frame(load(substitutions.get(name, name)))
        size = texture.shape[0]
        selected = mapping[..., 0] == source_index
        out[selected] = texture[mapping[..., 1][selected] % size, mapping[..., 2][selected] % size]
    return out
