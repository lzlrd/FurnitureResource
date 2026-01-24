from .BaseCompoment import BaseCompoment
import os

from PIL import Image


class BedCompoment(BaseCompoment):
    def __init__(self, overlay: str, dir: str) -> None:
        self.dir = "resources/" + dir + "/"
        self.overlay = overlay

    def run(self) -> None:
        x = -36
        os.makedirs(
            f"{self.output}/assets/minecraft/textures/entity/bed", exist_ok=True
        )
        with open("resources/" + self.overlay, "rb") as f:
            overlay = Image.open(f)
            overlay = overlay.convert("RGBA")
            overlay = overlay.resize((int(i / 3.3) for i in overlay.size))
            for item in os.listdir(self.dir):
                if item.endswith(".png"):
                    im = Image.open(self.dir + item)
                    im = im.convert("RGBA")
                    im = im.resize(
                        (
                            1024,
                            1024,
                        )
                    )
                    overlay1 = overlay.copy()
                    overlay1 = overlay1.crop((0, 0, overlay.size[0], 240))

                    overlay2 = overlay.copy()
                    overlay2 = overlay2.crop((0, 240, overlay.size[0], overlay.size[1]))
                    im.paste(overlay1, (x, 112), overlay1)
                    im.paste(overlay2, (x, 448), overlay2)
                    im.save(
                        f"{self.output}/assets/minecraft/textures/entity/bed/" + item
                    )
                    print("[bed.py] Generated " + item)
