from mcresourcelib import (
    Resourcepack,
    CustomModelCompoment
)
import os
import uuid
from variant_component import VariantModelCompoment
from variants import variants
from pfm_component import PfmModelCompoment, pfm_items
from icon_component import IconCompoment
namespace="cutebear_furniture"

info = {
    "pack": {
        "pack_format": 69,
        "description": "Cutebear's furniture resource pack",
        "min_format": [15, 0],
        "max_format": [1000, 0],
        "supported_formats": [15, 1000],
    }
}


info_be={
    "format_version": 2,
    "header": {
        "name": namespace,
        "description": "Cutebear's furniture resouce pack",
        "uuid": str(uuid.uuid4()),
        "version": [1, 0, 0],
        "min_engine_version": [1, 21, 110]
    },
    "metadata": {
        "authors": ["cutebear"]
    },
    "modules": [
        {
        "description": "Cutebear's furniture resouce pack",
            "type": "resources",
            "uuid": str(uuid.uuid4()),
            "version": [1, 0, 0]
        }
    ]
}
BASE_ITEM="poisonous_potato"

pack = Resourcepack(info, "pack.png",info_be)
pack.add(CustomModelCompoment("cutebear_furniture","chair",[],"chair.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","classic_desk_all",[],"classic_desk_all.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","classic_stool",[],"classic_stool.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","coffee_table_basic",[],"coffee_table_basic.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","dinner_table",[],"dinner_table.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","chair_classic",[],"chair_classic.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","chair_modern",[],"chair_modern.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","chair_dinner",[],"chair_dinner.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","bathtub",[],"bathtub.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","basic_sink",[],"basic_sink.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","white_arm_chair",[],"white_arm_chair.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","trash_can",[],"trash_can.png",BASE_ITEM))
pack.add(CustomModelCompoment("cutebear_furniture","toilet",[],"toilet.png",BASE_ITEM))

# Wood, wool and concrete variants. Regenerate their Bedrock textures with
# tools/generate_variant_textures.py after changing variants.py.
for item, parent, substitutions in variants():
    pack.add(VariantModelCompoment(namespace, item, parent, substitutions, BASE_ITEM))

# The rest of Paladin's furniture, imported with tools/import_pfm.py.
for item in pfm_items():
    pack.add(PfmModelCompoment(namespace, item, BASE_ITEM))

# Bedrock inventory icons drawn from each piece's geometry. Keep it after every piece.
pack.add(IconCompoment(namespace))


pack.run("../cutebear_furniture.zip")
pack.run_be("../cutebear_furniture.mcpack")
pack.generate_geyser("cutebear_furniture.json")

os.system(
    "cp cutebear_furniture.json /home/cutebear/paper12110_geyser/plugins/Geyser-Spigot/custom_mappings"
)

os.system(
    "cp ./cutebear_furniture.mcpack /home/cutebear/paper12110_geyser/plugins/Geyser-Spigot/packs"
)

os.system(
    "cp ./cutebear_furniture.zip /home/cutebear/.local/share/PrismLauncher/instances/1.21.10/minecraft/resourcepacks"
)
os.system("rm -f /tmp/reloadpack")
os.system("touch /tmp/reloadpack")
