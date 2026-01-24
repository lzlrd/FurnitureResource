from .BaseCompoment import BaseCompoment
import os

from PIL import Image


map = {
    "1x1": [
        "aztec",
        "aztec2",
        "alban",
        "bomb",
        "plant",
        "wasteland",
        "meditative",
        "kebab",
    ],
    "1x2": ["wanderer", "graham", "prairie_ride"],
    "2x1": ["pool", "courbet", "sea", "creebet", "sunset"],
    "2x2": [
        "match",
        "bust",
        "stage",
        "void",
        "skull_and_roses",
        "wither",
        "baroque",
        "humble",
    ],
    "3x3": [
        "bouquet",
        "cavebird",
        "cotan",
        "endboss",
        "fern",
        "owlemons",
        "sunflowers",
        "tides",
        "dennis",
    ],
    "4x2": ["fighters", "changing", "finding", "lowmist", "passage"],
    "3x4": ["backyard", "pond"],
    "4x3": ["skeleton", "donkey_kong"],
    "4x4": ["pointer", "pigscene", "burning_skull", "orb", "unpacked"],
}
resolution = {
    "1x1": (256, 256),
    "1x2": (256, 512),
    "4x2": (1024, 512),
    "2x1": (512, 256),
    "2x2": (512, 512),
    "3x3": (768, 768),
    "3x4": (768, 1024),
    "4x3": (1024, 768),
    "4x4": (1024, 1024),
}


class PaintingCompoment(BaseCompoment):
    def __init__(self, dir: str) -> None:
        self.dir = "resources/" + dir + "/"

    def run(self) -> None:
        os.makedirs(f"{self.output}/assets/minecraft/textures/painting", exist_ok=True)
        for size in os.listdir(self.dir):
            for i, file in enumerate(sorted(os.listdir(self.dir + size))):
                print(f"[painting.py] Adding {size}/{file} to {map[size][i]}")
                img = Image.open(self.dir + size + "/" + file)
                img.resize(resolution[size])
                img.save(
                    f"{self.output}/assets/minecraft/textures/painting/{map[size][i]}.png"
                )
