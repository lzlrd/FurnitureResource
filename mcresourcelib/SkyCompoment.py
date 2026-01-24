from .BaseCompoment import BaseCompoment
import os
import shutil

from PIL import Image


class SkyCompoment(BaseCompoment):
    def __init__(self, dir: str) -> None:
        self.dir = "resources/" + dir + "/"

    def run(self) -> None:
        os.makedirs(
            f"{self.output}/assets/minecraft/textures/environment", exist_ok=True
        )
        image = Image.new("RGB", (4096, 2048))
        print("[sky.py] generating moon")
        with open(f"{self.dir}/moon.png", "rb") as f:
            moon = Image.open(f)
            for y in range(2):
                for x in range(4):
                    image.paste(moon, (x * 1024, y * 1024))
        image.save(
            f"{self.output}/assets/minecraft/textures/environment/moon_phases.png"
        )
        shutil.copy(
            f"{self.dir}/sun.png",
            f"{self.output}/assets/minecraft/textures/environment/",
        )
