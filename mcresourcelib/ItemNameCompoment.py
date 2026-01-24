from .BaseCompoment import BaseCompoment
import shutil
import os
import json


class ItemNameCompoment(BaseCompoment):
    def __init__(self, item: str, name: str) -> None:
        self.item = item
        self.name = name

    def run(self) -> None:
        for i in os.listdir(f"resources/itemname/{self.item}/textures/"):
            shutil.copy(
                f"resources/itemname/{self.item}/textures/{i}",
                f"{self.output}/assets/minecraft/textures/item/",
            )
        shutil.copy(
            f"resources/itemname/{self.item}/{self.item}.json",
            f"{self.output}/assets/minecraft/models/item/",
        )


class ItemNameCompoments(BaseCompoment):
    def __init__(
        self, item: str, data: list[ItemNameCompoment], fallback: dict = {}
    ) -> None:
        self.item = item
        self.data = data
        if len(fallback) == 0:
            self.fallback = {
                "parent": "minecraft:item/handheld",
                "textures": {"layer0": f"minecraft:item/{item}"},
            }
        else:
            self.fallback = fallback

    def run(self) -> None:
        os.makedirs(f"{self.output}/assets/minecraft/items", exist_ok=True)
        os.makedirs(f"{self.output}/assets/minecraft/textures/item", exist_ok=True)
        os.makedirs(f"{self.output}/assets/minecraft/models/item", exist_ok=True)
        for i in self.data:
            i.run()
        data = {
            "model": {
                "type": "minecraft:condition",
                "property": "minecraft:has_component",
                "component": "minecraft:custom_name",
                "on_true": {
                    "type": "minecraft:select",
                    "property": "minecraft:component",
                    "component": "minecraft:custom_name",
                    "cases": [
                        {
                            "when": i.name,
                            "model": {
                                "type": "minecraft:model",
                                "model": f"minecraft:item/{i.item}",
                                "tints": [],
                            },
                        }
                        for i in self.data
                    ],
                    "fallback": {
                        "type": "minecraft:model",
                        "model": f"minecraft:item/{self.item}",
                    },
                },
                "on_false": {
                    "type": "minecraft:model",
                    "model": f"minecraft:item/{self.item}",
                },
            }
        }
        with open(f"{self.output}/assets/minecraft/items/{self.item}.json", "w") as f:
            json.dump(data, f)
        with open(
            f"{self.output}/assets/minecraft/models/item/{self.item}.json", "w"
        ) as f:
            json.dump(self.fallback, f)
