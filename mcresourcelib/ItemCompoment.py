from .BaseCompoment import BaseCompoment
import shutil
import os
import json


class ItemCompoment(BaseCompoment):
    def __init__(self, item: str) -> None:
        self.item = item

    def run(self) -> None:
        os.makedirs(f"{self.output}/assets/minecraft/textures/item", exist_ok=True)
        os.makedirs(f"{self.output}/assets/minecraft/models/item", exist_ok=True)
        shutil.copy(
            f"resources/items/{self.item}.png",
            f"{self.output}/assets/minecraft/textures/item/",
        )
        if os.path.isfile(f"resources/items/{self.item}.json"):
            shutil.copy(
                f"resources/items/{self.item}.json",
                f"{self.output}/assets/minecraft/models/item/",
            )
        else:
            with open(
                f"{self.output}/assets/minecraft/models/item/{self.item}.json", "w"
            ) as f:
                json.dump(
                    {
                        "parent": "item/generated",
                        "textures": {"layer0": f"item/{self.item}"},
                    },
                    f,
                )
