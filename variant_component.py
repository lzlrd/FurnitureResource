import json
import os
import shutil

from mcresourcelib import CustomModelCompoment


def texture_name(reference: str) -> str:
    return reference.split(":")[-1].removeprefix("block/")


class VariantModelCompoment(CustomModelCompoment):
    """A retextured copy of an existing furniture model.

    Java: a child model that inherits the parent's elements and swaps textures.
    Bedrock: the parent's geometry with a pre-generated texture from
    resources/customModel/variants (see tools/generate_variant_textures.py).
    """

    def __init__(
        self,
        namespace: str,
        item: str,
        parent: str,
        substitutions: dict[str, str],
        item_base: str,
    ) -> None:
        super().__init__(namespace, item, [], f"variants/{item}.png", item_base)
        self.parent = parent
        self.substitutions = substitutions

    def run(self) -> None:
        os.makedirs(f"{self.output}/assets/{self.namespace}/items", exist_ok=True)
        os.makedirs(f"{self.output}/assets/{self.namespace}/models", exist_ok=True)
        with open(f"{self.output}/assets/{self.namespace}/items/{self.item}.json", "w") as f:
            json.dump(
                {
                    "model": {
                        "type": "minecraft:model",
                        "model": f"{self.namespace}:{self.item}",
                    }
                },
                f,
            )
        with open(f"resources/customModel/{self.parent}.json") as f:
            parent_textures = json.load(f).get("textures", {})
        textures = {
            key: f"block/{self.substitutions[texture_name(value)]}"
            for key, value in parent_textures.items()
            if not value.startswith("#") and texture_name(value) in self.substitutions
        }
        with open(f"{self.output}/assets/{self.namespace}/models/{self.item}.json", "w") as f:
            json.dump({"parent": f"{self.namespace}:{self.parent}", "textures": textures}, f)

    def run_be(self) -> None:
        os.makedirs(f"{self.output_be}/textures", exist_ok=True)
        os.makedirs(f"{self.output_be}/attachables", exist_ok=True)
        shutil.copy(
            f"resources/customModel/{self.be_texture}",
            f"{self.output_be}/textures/{self.item}.png",
        )
        with open(f"{self.output_be}/attachables/{self.item}.json", "w") as f:
            json.dump(
                {
                    "format_version": "1.21.0",
                    "minecraft:attachable": {
                        "description": {
                            "identifier": f"{self.namespace}:{self.item}",
                            "materials": {
                                "default": "entity_alphatest",
                                "enchanted": "entity_alphatest_glint",
                            },
                            "textures": {
                                "default": f"textures/{self.item}",
                                "enchanted": "textures/misc/enchanted_item_glint",
                            },
                            "geometry": {"default": f"geometry.{self.parent}"},
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
        item_texture = {
            "resource_pack_name": self.namespace,
            "texture_data": {},
            "texture_name": "atlas.items",
        }
        try:
            with open(f"{self.output_be}/textures/item_texture.json") as f:
                item_texture = json.load(f)
        except Exception:
            pass
        item_texture["texture_data"][f"{self.namespace}.{self.item}"] = {
            "textures": f"textures/{self.item}"
        }
        with open(f"{self.output_be}/textures/item_texture.json", "w") as f:
            json.dump(item_texture, f)
