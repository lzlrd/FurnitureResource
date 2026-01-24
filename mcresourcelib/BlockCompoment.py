from .BaseCompoment import BaseCompoment
import shutil
import os


class BlockCompoment(BaseCompoment):
    def __init__(self, item: str) -> None:
        self.item = item

    def run(self) -> None:
        os.makedirs(f"{self.output}/assets/minecraft/textures/block", exist_ok=True)
        shutil.copy(
            f"resources/blocks/{self.item}.png",
            f"{self.output}/assets/minecraft/textures/block/",
        )
