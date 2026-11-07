import json
import os
import shutil

from mcresourcelib import CustomModelCompoment

PFM = "resources/pfm"


class PfmModelCompoment(CustomModelCompoment):
    """A piece imported from Paladin's Furniture by tools/import_pfm.py.

    Java: the imported model, with the Paladin textures it uses under block/pfm/.
    Bedrock: the imported geometry and atlas, with the same attachable as the other pieces.
    """

    def __init__(self, namespace: str, item: str, item_base: str) -> None:
        super().__init__(namespace, item, [], f"pfm/{item}.png", item_base)

    def run(self) -> None:
        os.makedirs(f"{self.output}/assets/{self.namespace}/items", exist_ok=True)
        os.makedirs(f"{self.output}/assets/{self.namespace}/models", exist_ok=True)
        with open(f"{self.output}/assets/{self.namespace}/items/{self.item}.json", "w") as f:
            json.dump({"model": {"type": "minecraft:model", "model": f"{self.namespace}:{self.item}"}}, f)
        shutil.copy(f"{PFM}/models/{self.item}.json", f"{self.output}/assets/{self.namespace}/models/{self.item}.json")
        textures = f"{self.output}/assets/{self.namespace}/textures/block/pfm"
        if not os.path.isdir(textures):
            shutil.copytree(f"{PFM}/textures", textures)

    def run_be(self) -> None:
        os.makedirs(f"{self.output_be}/models/entity", exist_ok=True)
        os.makedirs(f"{self.output_be}/textures/pfm", exist_ok=True)
        os.makedirs(f"{self.output_be}/attachables", exist_ok=True)
        shutil.copy(f"{PFM}/bedrock/{self.item}.geo.json", f"{self.output_be}/models/entity/{self.item}.geo.json")
        shutil.copy(f"{PFM}/bedrock/{self.item}.png", f"{self.output_be}/textures/pfm/{self.item}.png")
        texture = f"textures/pfm/{self.item}"
        with open(f"{self.output_be}/attachables/{self.item}.json", "w") as f:
            json.dump(
                {
                    "format_version": "1.21.0",
                    "minecraft:attachable": {
                        "description": {
                            "identifier": f"{self.namespace}:{self.item}",
                            "materials": {"default": "entity_alphatest", "enchanted": "entity_alphatest_glint"},
                            "textures": {"default": texture, "enchanted": "textures/misc/enchanted_item_glint"},
                            "geometry": {"default": f"geometry.{self.item}"},
                            "render_controllers": ["controller.render.item_default"],
                            "scripts": {
                                "parent_setup": "variable.is_first_person = 0.0;",
                                "animate": [
                                    {"wield_third_person": "!variable.is_first_person"},
                                    {"wield_first_person": "variable.is_first_person"},
                                ],
                            },
                            "animations": {
                                "wield_third_person": "animation.humanoid.wield_third_person_dowsing_rod",
                                "wield_first_person": "animation.humanoid.wield_first_person_dowsing_rod",
                            },
                        }
                    },
                },
                f,
            )
        item_texture = {"resource_pack_name": self.namespace, "texture_data": {}, "texture_name": "atlas.items"}
        try:
            with open(f"{self.output_be}/textures/item_texture.json") as f:
                item_texture = json.load(f)
        except Exception:
            pass
        item_texture["texture_data"][f"{self.namespace}.{self.item}"] = {"textures": texture}
        with open(f"{self.output_be}/textures/item_texture.json", "w") as f:
            json.dump(item_texture, f)


def pfm_items() -> list[str]:
    with open(f"{PFM}/furniture.json") as f:
        return [entry["id"] for entry in json.load(f)["items"]]
