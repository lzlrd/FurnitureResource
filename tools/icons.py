"""Inventory icons for Bedrock, rendered from each item's geometry and texture atlas.

Bedrock shows an item's item_texture in inventories, and without an icon that was the atlas itself. This draws the
piece as it stands when placed in front of the player, seen from above and to the side like a block in a Java
inventory.

The geometry follows the pack's convention (tools/pfm.py): x is mirrored about the block's centre, and each face's
part of the atlas holds the face as Java shows it. So the renderer turns each cube back into its Java element and lays
its faces out the way Java does.
"""

import json
import math
from pathlib import Path

import numpy as np
from PIL import Image

SIZE = 64
SUPERSAMPLE = 4
FILL = 0.9
# Viewed from the front and to the right of a piece placed facing the viewer, tilted like a block in a Java inventory.
TURN = math.radians(-45)
TILT = math.radians(30)


def geometry_cubes(path: Path) -> dict:
    """Each geometry in a .geo.json file, by identifier: its cubes, which carry no bone rotation in this pack."""
    data = json.loads(Path(path).read_text())
    result = {}
    for geometry in data["minecraft:geometry"]:
        cubes = []
        for bone in geometry.get("bones", []):
            if any(bone.get("rotation") or [0, 0, 0]):
                raise ValueError(f"bone rotation in {path}")
            cubes.extend(bone.get("cubes", []))
        result[geometry["description"]["identifier"]] = cubes
    return result


def java_element(cube: dict):
    """The Java element a cube came from: its low and high corners and its rotation, if any."""
    origin, size = cube["origin"], cube["size"]
    high_x = 8 - origin[0]
    low = np.array([high_x - size[0], origin[1], origin[2] + 8], dtype=float)
    high = np.array([high_x, origin[1] + size[1], origin[2] + 8 + size[2]], dtype=float)
    rotation = None
    angles = cube.get("rotation")
    if angles and any(angles):
        pivot = cube.get("pivot", [0, 0, 0])
        centre = np.array([8 - pivot[0], pivot[1], pivot[2] + 8], dtype=float)
        if angles[0]:
            rotation = ("x", -angles[0], centre)
        elif angles[1]:
            rotation = ("y", angles[1], centre)
        else:
            rotation = ("z", angles[2], centre)
    return low, high, rotation


def face_corners(face: str, lo, hi):
    """Top left, top right and bottom left of a face as Java lays its texture out, and the face's normal."""
    x1, y1, z1 = lo
    x2, y2, z2 = hi
    return {
        "north": ((x2, y2, z1), (x1, y2, z1), (x2, y1, z1), (0, 0, -1)),
        "south": ((x1, y2, z2), (x2, y2, z2), (x1, y1, z2), (0, 0, 1)),
        "west": ((x1, y2, z1), (x1, y2, z2), (x1, y1, z1), (-1, 0, 0)),
        "east": ((x2, y2, z2), (x2, y2, z1), (x2, y1, z2), (1, 0, 0)),
        "up": ((x1, y2, z1), (x2, y2, z1), (x1, y2, z2), (0, 1, 0)),
        "down": ((x1, y1, z2), (x2, y1, z2), (x1, y1, z1), (0, -1, 0)),
    }[face]


def rotate(points: np.ndarray, rotation) -> np.ndarray:
    """Java's element rotation: right-handed about the axis through its origin."""
    if rotation is None:
        return points
    axis, angle, centre = rotation
    c, s = math.cos(math.radians(angle)), math.sin(math.radians(angle))
    p = points - centre
    if axis == "x":
        m = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    elif axis == "y":
        m = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    else:
        m = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
    return p @ m.T + centre


def placement(yaw_offset: int) -> np.ndarray:
    """Model to world for a piece placed in front of a viewer who stands south of it. The plugin gives the display the
    yaw 270 plus the piece's offset, and an item display at yaw 0, 90, 180 or 270 points the model's x axis west, north,
    east or south."""
    quarter = round(((270 + yaw_offset) % 360) / 90) % 4
    x_axis = [(-1, 0, 0), (0, 0, -1), (1, 0, 0), (0, 0, 1)][quarter]
    z_axis = [(0, 0, -1), (1, 0, 0), (0, 0, 1), (-1, 0, 0)][quarter]
    return np.array([x_axis, (0, 1, 0), z_axis], dtype=float).T


def view() -> np.ndarray:
    turn = np.array([[math.cos(TURN), 0, math.sin(TURN)], [0, 1, 0], [-math.sin(TURN), 0, math.cos(TURN)]])
    tilt = np.array([[1, 0, 0], [0, math.cos(TILT), -math.sin(TILT)], [0, math.sin(TILT), math.cos(TILT)]])
    return tilt @ turn


def shade(normal) -> float:
    x, y, z = normal
    if y > 0.5:
        return 1.0
    if y < -0.5:
        return 0.5
    return 0.8 if abs(z) >= abs(x) else 0.62


def render(cubes: list, atlas: Image.Image, yaw_offset: int = 0, size: int = SIZE) -> Image.Image:
    """An icon for a piece: its cubes, the atlas their faces use, and the yaw offset the plugin places it with."""
    atlas = np.asarray(atlas.convert("RGBA"), dtype=np.float32)
    atlas_h, atlas_w = atlas.shape[:2]
    to_world = placement(yaw_offset)
    camera = view()
    faces = []
    for cube in cubes:
        uv = cube.get("uv")
        if not isinstance(uv, dict):
            continue
        low, high, rotation = java_element(cube)
        centre = np.array([8, 0, 8], dtype=float)
        for face, region in uv.items():
            u, v = region["uv"]
            w, h = region["uv_size"]
            if w < 0:
                u, w = u + w, -w
            if h < 0:
                v, h = v + h, -h
            if w <= 0 or h <= 0:
                continue
            tl, tr, bl, normal = face_corners(face, low, high)
            points = rotate(np.array([tl, tr, bl], dtype=float), rotation)
            n = rotate(np.array([normal], dtype=float), (rotation[0], rotation[1], np.zeros(3)) if rotation else None)[0]
            world = (points - centre) @ to_world.T
            world_normal = n @ to_world.T
            screen = world @ camera.T
            if (world_normal @ camera.T)[2] <= 1e-6:
                continue
            faces.append((screen, (u, v, w, h), shade(world_normal)))
    if not faces:
        return Image.new("RGBA", (size, size), (0, 0, 0, 0))
    corners = []
    for screen, *_ in faces:
        tl, tr, bl = screen
        corners.extend([tl, tr, bl, tr + bl - tl])
    corners = np.array(corners)
    lo, hi = corners[:, :2].min(axis=0), corners[:, :2].max(axis=0)
    big = size * SUPERSAMPLE
    scale = FILL * big / max(hi - lo)
    offset = (np.array([big, big]) - (hi - lo) * scale) / 2
    colour = np.zeros((big, big, 4), dtype=np.float32)
    depth = np.full((big, big), -np.inf, dtype=np.float32)
    for screen, (u, v, w, h), light in faces:
        p = np.empty((3, 2))
        p[:, 0] = (screen[:, 0] - lo[0]) * scale + offset[0]
        p[:, 1] = big - ((screen[:, 1] - lo[1]) * scale + offset[1])
        z = screen[:, 2]
        e1, e2 = p[1] - p[0], p[2] - p[0]
        det = e1[0] * e2[1] - e1[1] * e2[0]
        if abs(det) < 1e-9:
            continue
        quad = np.array([p[0], p[1], p[2], p[1] + p[2] - p[0]])
        x0, y0 = np.floor(quad.min(axis=0)).astype(int)
        x1, y1 = np.ceil(quad.max(axis=0)).astype(int)
        x0, y0, x1, y1 = max(x0, 0), max(y0, 0), min(x1, big), min(y1, big)
        if x0 >= x1 or y0 >= y1:
            continue
        ys, xs = np.mgrid[y0:y1, x0:x1]
        dx, dy = xs + 0.5 - p[0][0], ys + 0.5 - p[0][1]
        s = (dx * e2[1] - dy * e2[0]) / det
        t = (dy * e1[0] - dx * e1[1]) / det
        inside = (s >= 0) & (s <= 1) & (t >= 0) & (t <= 1)
        if not inside.any():
            continue
        d = z[0] + s * (z[1] - z[0]) + t * (z[2] - z[0])
        tex_x = np.clip(np.floor(u + s * w), 0, atlas_w - 1).astype(int)
        tex_y = np.clip(np.floor(v + t * h), 0, atlas_h - 1).astype(int)
        texel = atlas[tex_y, tex_x]
        mask = inside & (texel[..., 3] >= 128) & (d > depth[y0:y1, x0:x1])
        if not mask.any():
            continue
        region_depth = depth[y0:y1, x0:x1]
        region_colour = colour[y0:y1, x0:x1]
        region_depth[mask] = d[mask]
        lit = texel.copy()
        lit[..., :3] *= light
        lit[..., 3] = 255
        region_colour[mask] = lit[mask]
    image = Image.fromarray(np.clip(colour, 0, 255).astype(np.uint8), "RGBA")
    return image.resize((size, size), Image.Resampling.BOX)
