"""Turn Paladin's Furniture block models into furniture for this pack.

A Paladin model becomes a flattened Java model, whose Paladin textures are copied into the pack under
cutebear_furniture:block/pfm/, and Bedrock geometry with a texture atlas baked from the faces it shows. The geometry
follows Blockbench's Bedrock export, which made the pack's first models: x is mirrored about the block's centre,
one bone holds every cube, and each face gets its own part of the atlas.
"""

import io
import json
import zipfile
from pathlib import Path

from PIL import Image

NAMESPACE = "cutebear_furniture"
FACES = ("north", "east", "south", "west", "up", "down")


def split(reference: str) -> tuple:
    namespace, path = reference.split(":", 1) if ":" in reference else ("minecraft", reference)
    return namespace, path


class Sources:
    """Models and textures from Paladin's assets/pfm folder and a vanilla client jar."""

    def __init__(self, pfm_assets: Path, client_jar: Path):
        self.pfm = Path(pfm_assets)
        self.jar = zipfile.ZipFile(client_jar)
        self.images = {}

    def model(self, reference: str) -> dict:
        namespace, path = split(reference)
        if namespace == "pfm":
            return json.loads((self.pfm / "models" / f"{path}.json").read_text())
        return json.loads(self.jar.read(f"assets/minecraft/models/{path}.json"))

    def texture_bytes(self, reference: str) -> bytes:
        namespace, path = split(reference)
        if namespace == "pfm":
            return (self.pfm / "textures" / f"{path}.png").read_bytes()
        return self.jar.read(f"assets/minecraft/textures/{path}.png")

    def image(self, reference: str) -> Image.Image:
        if reference not in self.images:
            image = Image.open(io.BytesIO(self.texture_bytes(reference))).convert("RGBA")
            if image.height > image.width:
                # Animated textures are a strip of square frames; Bedrock gets the first.
                image = image.crop((0, 0, image.width, image.width))
            self.images[reference] = image
        return self.images[reference]


def flatten(sources: Sources, reference: str, textures: dict | None = None) -> dict:
    """The model with its parents folded in: the nearest elements, and textures and display merged child-first."""
    chain = []
    while reference:
        model = sources.model(reference)
        chain.append(model)
        reference = model.get("parent")
        if reference and split(reference)[1].startswith("builtin/"):
            break
    merged = {"textures": {}, "display": {}}
    for model in reversed(chain):
        merged["textures"].update(model.get("textures", {}))
        merged["display"].update(model.get("display", {}))
        if "elements" in model:
            merged["elements"] = model["elements"]
    merged["textures"].update(textures or {})
    if "elements" not in merged:
        raise ValueError(f"{reference} has no elements")
    return merged


def resolve(textures: dict, reference: str | None) -> str | None:
    seen = set()
    while reference and reference.startswith("#"):
        key = reference[1:]
        if key in seen:
            return None
        seen.add(key)
        reference = textures.get(key)
    if reference is None:
        return None
    namespace, path = split(reference)
    return f"{namespace}:{path}"


def pack_texture(reference: str) -> str:
    """Where a texture lives for Java: vanilla ones stay, Paladin's move into this pack."""
    namespace, path = split(reference)
    if namespace == "pfm":
        return f"{NAMESPACE}:block/pfm/{path.removeprefix('block/')}"
    return f"minecraft:{path}"


def java_model(model: dict) -> tuple:
    """The flattened model for the pack, and the Paladin textures it needs."""
    textures, needed = {}, set()
    for key in model["textures"]:
        concrete = resolve(model["textures"], f"#{key}")
        if concrete is None:
            continue
        textures[key] = pack_texture(concrete)
        if concrete.startswith("pfm:"):
            needed.add(concrete)
    elements = []
    for element in model["elements"]:
        element = {k: v for k, v in element.items() if k in ("from", "to", "rotation", "faces", "shade", "light_emission")}
        faces = {}
        for face, data in element["faces"].items():
            data = {k: v for k, v in data.items() if k != "tintindex"}
            faces[face] = data
        element["faces"] = faces
        elements.append(element)
    result = {"credit": "By UnlikePaladin", "textures": textures, "elements": elements}
    if model["display"]:
        result["display"] = model["display"]
    return result, needed


def default_uv(element: dict, face: str) -> list:
    (x1, y1, z1), (x2, y2, z2) = element["from"], element["to"]
    return {
        "down": [x1, 16 - z2, x2, 16 - z1],
        "up": [x1, z1, x2, z2],
        "north": [16 - x2, 16 - y2, 16 - x1, 16 - y1],
        "south": [x1, 16 - y2, x2, 16 - y1],
        "west": [z1, 16 - y2, z2, 16 - y1],
        "east": [16 - z2, 16 - y2, 16 - z1, 16 - y1],
    }[face]


def face_image(texture: Image.Image, uv: list, rotation: int) -> Image.Image:
    """What Java shows on a face: the uv rectangle, flipped when it runs backwards, turned clockwise by rotation."""
    unit = texture.width / 16
    u1, v1, u2, v2 = uv
    left, right = sorted((round(u1 * unit), round(u2 * unit)))
    top, bottom = sorted((round(v1 * unit), round(v2 * unit)))
    right, bottom = max(right, left + 1), max(bottom, top + 1)
    region = texture.crop((left, top, right, bottom))
    if u1 > u2:
        region = region.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
    if v1 > v2:
        region = region.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
    if rotation % 360:
        region = region.rotate(-rotation, expand=True)
    return region


def pack_regions(images: list) -> tuple:
    """Shelf-pack images into the smallest power-of-two atlas found. Identical images share a place."""
    unique, index = {}, []
    for image in images:
        key = (image.size, image.tobytes())
        if key not in unique:
            unique[key] = image
        index.append(key)
    order = sorted(unique, key=lambda k: (-k[0][1], -k[0][0]))
    width = 16
    while True:
        positions, x, y, shelf = {}, 0, 0, 0
        for key in order:
            w, h = key[0]
            if w > width:
                break
            if x + w > width:
                x, y, shelf = 0, y + shelf, 0
            positions[key] = (x, y)
            x += w
            shelf = max(shelf, h)
        else:
            height = 16
            while height < y + shelf:
                height *= 2
            if height <= width * 2:
                break
        width *= 2
    atlas = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for key, (x, y) in positions.items():
        atlas.paste(unique[key], (x, y))
    return atlas, [positions[key] for key in index]


def number(value: float):
    value = round(value, 5)
    return int(value) if value == int(value) else value


def cube(element: dict) -> dict:
    low = [min(a, b) for a, b in zip(element["from"], element["to"])]
    high = [max(a, b) for a, b in zip(element["from"], element["to"])]
    result = {
        "origin": [number(8 - high[0]), number(low[1]), number(low[2] - 8)],
        "size": [number(h - l) for l, h in zip(low, high)],
    }
    rotation = element.get("rotation")
    if rotation and rotation.get("angle"):
        axis, angle, origin = rotation["axis"], rotation["angle"], rotation["origin"]
        result["pivot"] = [number(8 - origin[0]), number(origin[1]), number(origin[2] - 8)]
        result["rotation"] = [number(-angle) if axis == "x" else 0, number(angle) if axis == "y" else 0,
                              number(angle) if axis == "z" else 0]
    return result


def bake(sources: Sources, model: dict, identifier: str) -> tuple:
    """Bedrock geometry and its atlas for a flattened model."""
    faces = []
    for number_, element in enumerate(model["elements"]):
        for face, data in element.get("faces", {}).items():
            texture = resolve(model["textures"], data.get("texture"))
            if texture is None:
                continue
            uv = data.get("uv") or default_uv(element, face)
            faces.append((number_, face, face_image(sources.image(texture), uv, data.get("rotation", 0))))
    atlas, places = pack_regions([image for _, _, image in faces])
    cubes = [cube(element) for element in model["elements"]]
    for (number_, face, image), (x, y) in zip(faces, places):
        w, h = image.size
        if face in ("up", "down"):
            uv = {"uv": [x + w, y + h], "uv_size": [-w, -h]}
        else:
            uv = {"uv": [x, y], "uv_size": [w, h]}
        cubes[number_].setdefault("uv", {})[face] = uv
    cubes = [c for c in cubes if "uv" in c]
    low = [min(c["origin"][i] for c in cubes) for i in range(3)]
    high = [max(c["origin"][i] + c["size"][i] for c in cubes) for i in range(3)]
    reach = max(abs(low[0]), abs(high[0]), abs(low[2]), abs(high[2]))
    geometry = {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": f"geometry.{identifier}",
                "texture_width": atlas.width,
                "texture_height": atlas.height,
                "visible_bounds_width": number(max(2, 2 * reach / 16 + 1)),
                "visible_bounds_height": number(max(2, (high[1] - min(low[1], 0)) / 16 + 1)),
                "visible_bounds_offset": [0, number((high[1] + low[1]) / 32), 0],
            },
            "bones": [{"name": identifier, "pivot": [8, 0, -8], "cubes": cubes}],
        }],
    }
    return geometry, atlas
