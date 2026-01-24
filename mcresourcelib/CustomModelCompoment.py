from .BaseCompoment import BaseCompoment
import shutil
import os
import json


class CustomModelCompoment(BaseCompoment):
    def __init__(self, namespace: str, item: str, textures: list[str]) -> None:
        self.item = item
        self.namespace = namespace
        self.textures = textures

    def run(self) -> None:
        os.makedirs(f"{self.output}/assets/{self.namespace}/items", exist_ok=True)
        os.makedirs(
            f"{self.output}/assets/{self.namespace}/textures/item/", exist_ok=True
        )
        os.makedirs(f"{self.output}/assets/{self.namespace}/models", exist_ok=True)
        data = {
            "model": {
                "type": "minecraft:model",
                "model": f"{self.namespace}:{self.item}",
            }
        }

        with open(
            f"{self.output}/assets/{self.namespace}/items/{self.item}.json", "w"
        ) as f:
            json.dump(data, f)
        for texture in self.textures:
            shutil.copy(
                f"resources/customModel/{texture}",
                f"{self.output}/assets/{self.namespace}/textures/item/",
            )
        shutil.copy(
            f"resources/customModel/{self.item}.json",
            f"{self.output}/assets/{self.namespace}/models/",
        )
