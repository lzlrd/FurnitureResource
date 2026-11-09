import glob
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from PIL import Image

from mcresourcelib.BaseCompoment import BaseCompoment

sys.path.insert(0, str(Path(__file__).resolve().parent / "tools"))
import icons  # noqa: E402

PFM = "resources/pfm"


def _render(job: tuple) -> None:
    cubes, texture, yaw_offset, target = job
    icons.render(cubes, Image.open(texture), yaw_offset).save(target, optimize=True)


class IconCompoment(BaseCompoment):
    """Bedrock inventory icons. Add it after every piece: it draws each attachable's geometry with its texture, as the
    piece stands when placed, and points the piece's item_texture entry at the drawing instead of the atlas."""

    def __init__(self, namespace: str) -> None:
        super().__init__()
        self.namespace = namespace

    def run_be(self) -> None:
        geometries = {}
        for path in glob.glob(f"{self.output_be}/models/entity/*.geo.json"):
            geometries.update(icons.geometry_cubes(Path(path)))
        with open(f"{PFM}/furniture.json") as f:
            yaw = {entry["id"]: entry["yaw_offset"] for entry in json.load(f)["items"]}
        with open(f"{self.output_be}/textures/item_texture.json") as f:
            item_texture = json.load(f)
        os.makedirs(f"{self.output_be}/textures/icons", exist_ok=True)
        jobs = []
        for path in sorted(glob.glob(f"{self.output_be}/attachables/*.json")):
            with open(path) as f:
                description = json.load(f)["minecraft:attachable"]["description"]
            namespace, item = description["identifier"].split(":", 1)
            if namespace != self.namespace:
                continue
            cubes = geometries[description["geometry"]["default"]]
            texture = f"{self.output_be}/{description['textures']['default']}.png"
            jobs.append((cubes, texture, yaw.get(item, 0), f"{self.output_be}/textures/icons/{item}.png"))
            item_texture["texture_data"][f"{namespace}.{item}"] = {"textures": f"textures/icons/{item}"}
        with ProcessPoolExecutor() as pool:
            list(pool.map(_render, jobs, chunksize=32))
        with open(f"{self.output_be}/textures/item_texture.json", "w") as f:
            json.dump(item_texture, f)
