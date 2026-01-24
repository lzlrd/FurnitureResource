from PIL.ImageFile import ImageFile
from .BaseCompoment import BaseCompoment
import os

from PIL import Image

SIZE = 1024
# a clusterfuck but it work enough
CORDS = [
    (0, SIZE, SIZE, SIZE * 2),
    (SIZE, SIZE, SIZE * 2, SIZE * 2),
    (SIZE * 2, SIZE, SIZE * 3, SIZE * 2),
    (SIZE * 3, SIZE, SIZE * 4, SIZE * 2),
    (0, 0, SIZE, SIZE),
    (0, SIZE * 2, SIZE, SIZE * 3),
]


class PanoramaCompoment(BaseCompoment):
    def __init__(self) -> None:
        pass

    def split(self, index: int, image: ImageFile):
        image.crop(CORDS[index]).save(
            f"{self.output}/assets/minecraft/textures/gui/title/background/panorama_{index}.png"
        )

    def run(self) -> None:
        os.makedirs(
            f"{self.output}/assets/minecraft/textures/gui/title/background",
            exist_ok=True,
        )
        with open("resources/panorama.png", "rb") as f:
            image = Image.open(f)
            for i in range(6):
                self.split(i, image)
