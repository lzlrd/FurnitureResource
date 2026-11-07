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
        self.generated = {}

    def model(self, reference: str) -> dict:
        namespace, path = split(reference)
        if namespace == "pfm":
            return json.loads((self.pfm / "models" / f"{path}.json").read_text())
        return json.loads(self.jar.read(f"assets/minecraft/models/{path}.json"))

    def texture_bytes(self, reference: str) -> bytes:
        if reference in self.generated:
            buffer = io.BytesIO()
            self.generated[reference].save(buffer, "PNG", optimize=True)
            return buffer.getvalue()
        namespace, path = split(reference)
        if namespace == "pfm":
            return (self.pfm / "textures" / f"{path}.png").read_bytes()
        return self.jar.read(f"assets/minecraft/textures/{path}.png")

    def image(self, reference: str) -> Image.Image:
        if reference in self.generated:
            return self.generated[reference]
        if reference not in self.images:
            image = Image.open(io.BytesIO(self.texture_bytes(reference))).convert("RGBA")
            if image.height > image.width:
                # Animated textures are a strip of square frames; Bedrock gets the first.
                image = image.crop((0, 0, image.width, image.width))
            self.images[reference] = image
        return self.images[reference]

    def tinted(self, reference: str, colour: int, name: str) -> str:
        """The texture multiplied by a colour, as Minecraft tints a face, kept as a texture of this pack."""
        path = f"{split(reference)[1]}_{name}"
        generated = f"gen:{path}"
        if generated not in self.generated:
            red, green, blue, alpha = self.image(reference).split()
            factors = (colour >> 16 & 255, colour >> 8 & 255, colour & 255)
            channels = [channel.point(lambda value, factor=factor: value * factor // 255)
                        for channel, factor in zip((red, green, blue), factors)]
            self.generated[generated] = Image.merge("RGBA", (*channels, alpha))
        return generated


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


def compose(sources: Sources, parts: list) -> dict:
    """Several models as one, each part's texture keys prefixed with its index so parts can't clash. A part is a
    model reference or a model with elements and textures of its own. The first part's display is kept."""
    merged = {"textures": {}, "display": {}, "elements": []}
    for index, part in enumerate(parts):
        model = flatten(sources, part) if isinstance(part, str) else part
        prefix = f"p{index}_"
        for key, value in model["textures"].items():
            merged["textures"][prefix + key] = "#" + prefix + value[1:] if value.startswith("#") else value
        if index == 0:
            merged["display"] = dict(model.get("display", {}))
        for element in model["elements"]:
            element = json.loads(json.dumps(element))
            for data in element.get("faces", {}).values():
                if data.get("texture", "").startswith("#"):
                    data["texture"] = "#" + prefix + data["texture"][1:]
            merged["elements"].append(element)
    return merged


def retexture(sources: Sources, model: dict, substitutions: dict) -> dict:
    """The model with textures swapped. substitutions maps a texture as resolve() gives it to its replacement, or to
    ("tint", colour, name) for a tinted copy."""
    textures = {}
    for key, value in model["textures"].items():
        concrete = resolve(model["textures"], f"#{key}")
        replacement = substitutions.get(concrete)
        if isinstance(replacement, tuple):
            _, colour, name = replacement
            replacement = sources.tinted(concrete, colour, name)
        textures[key] = replacement or value
    return {**model, "textures": textures}


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
    if namespace in ("pfm", "gen"):
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
        if concrete.startswith(("pfm:", "gen:")):
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


def pack_regions(images: list, keys: list | None = None) -> tuple:
    """Shelf-pack images into the smallest power-of-two atlas found. Identical images, or images with equal keys when
    keys are given, share a place."""
    unique, index = {}, []
    for number_, image in enumerate(images):
        key = (image.size, keys[number_] if keys else image.tobytes())
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


def faces_of(model: dict) -> list:
    """Each face the model shows: its element's index, its side, and its texture, uv and rotation."""
    faces = []
    for number_, element in enumerate(model["elements"]):
        for face, data in element.get("faces", {}).items():
            texture = resolve(model["textures"], data.get("texture"))
            if texture is None:
                continue
            uv = tuple(data.get("uv") or default_uv(element, face))
            faces.append((number_, face, texture, uv, data.get("rotation", 0)))
    return faces


def geometry_for(model: dict, identifier: str, size: tuple, placed: list) -> dict:
    """Bedrock geometry for a flattened model whose faces sit in an atlas of this size: placed holds each face's
    element index, side, place in the atlas and size there."""
    cubes = [cube(element) for element in model["elements"]]
    for number_, face, (x, y), (w, h) in placed:
        if face in ("up", "down"):
            uv = {"uv": [x + w, y + h], "uv_size": [-w, -h]}
        else:
            uv = {"uv": [x, y], "uv_size": [w, h]}
        cubes[number_].setdefault("uv", {})[face] = uv
    cubes = [c for c in cubes if "uv" in c]
    low = [min(c["origin"][i] for c in cubes) for i in range(3)]
    high = [max(c["origin"][i] + c["size"][i] for c in cubes) for i in range(3)]
    reach = max(abs(low[0]), abs(high[0]), abs(low[2]), abs(high[2]))
    return {
        "format_version": "1.12.0",
        "minecraft:geometry": [{
            "description": {
                "identifier": f"geometry.{identifier}",
                "texture_width": size[0],
                "texture_height": size[1],
                "visible_bounds_width": number(max(2, 2 * reach / 16 + 1)),
                "visible_bounds_height": number(max(2, (high[1] - min(low[1], 0)) / 16 + 1)),
                "visible_bounds_offset": [0, number((high[1] + low[1]) / 32), 0],
            },
            "bones": [{"name": identifier, "pivot": [8, 0, -8], "cubes": cubes}],
        }],
    }


def bake(sources: Sources, model: dict, identifier: str) -> tuple:
    """Bedrock geometry and its atlas for a flattened model."""
    faces = faces_of(model)
    images = [face_image(sources.image(texture), uv, rotation) for _, _, texture, uv, rotation in faces]
    atlas, places = pack_regions(images)
    placed = [(number_, face, place, image.size) for (number_, face, *_), place, image in zip(faces, places, images)]
    return geometry_for(model, identifier, atlas.size, placed), atlas


def bake_family(sources: Sources, template: dict, variants: dict, identifier: str) -> tuple:
    """One Bedrock geometry for a family's template, and an atlas in its layout for each retextured variant. Faces
    share a place by their template texture, uv and rotation, so the layout fits every variant."""
    faces = faces_of(template)
    images = [face_image(sources.image(texture), uv, rotation) for _, _, texture, uv, rotation in faces]
    atlas, places = pack_regions(images, [(texture, uv, rotation) for _, _, texture, uv, rotation in faces])
    placed = [(number_, face, place, image.size) for (number_, face, *_), place, image in zip(faces, places, images)]
    atlases = {}
    for name, model in variants.items():
        canvas = Image.new("RGBA", atlas.size, (0, 0, 0, 0))
        for (_, _, texture, uv, rotation), place, image in zip(faces_of(model), places, images):
            region = face_image(sources.image(texture), uv, rotation)
            if region.size != image.size:
                region = region.resize(image.size, Image.Resampling.NEAREST)
            canvas.paste(region, place)
        atlases[name] = canvas
    return geometry_for(template, identifier, atlas.size, placed), atlases
