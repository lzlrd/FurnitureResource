from .BaseCompoment import BaseCompoment
import os
import json
from .ItemCompoment import ItemCompoment


class ItemModelCompoment(BaseCompoment):
    def __init__(self, item: str, model: dict) -> None:
        self.item = item
        self.model = model

    def run(self) -> None:
        os.makedirs(f"{self.output}/assets/minecraft/items", exist_ok=True)
        with open(f"{self.output}/assets/minecraft/items/{self.item}.json", "w") as f:
            json.dump(self.model, f)


class CustomItemCompoment(ItemModelCompoment):
    def __init__(self, item: str) -> None:
        """
        create a custom item model, can be obtain with item_model model compoment
        """
        self.item = item
        super().__init__(
            item,
            {
                "model": {
                    "type": "minecraft:model",
                    "model": f"minecraft:item/{self.item}",
                }
            },
        )

    def run(self) -> None:
        ItemCompoment(self.item).run()
        super().run()
