from mcresourcelib import (
    Resourcepack,
    CustomModelCompoment
)
import os

info = {
    "pack": {
        "pack_format": 69,
        "description": "Cutebear's furniture resource pack",
        "min_format": [15, 0],
        "max_format": [1000, 0],
        "supported_formats": [15, 1000],
    }
}

pack = Resourcepack(info, "pack.png")
pack.add(CustomModelCompoment("cutebear_furniture","chair",[]))
pack.add(CustomModelCompoment("cutebear_furniture","classic_desk_all",[]))
pack.add(CustomModelCompoment("cutebear_furniture","classic_stool",[]))
pack.add(CustomModelCompoment("cutebear_furniture","coffee_table_basic",[]))
pack.add(CustomModelCompoment("cutebear_furniture","dinner_table",[]))
pack.run("../cutebear_furniture.zip")

os.system(
    "rm -f /home/cutebear/.local/share/PrismLauncher/instances/1.21.10/minecraft/resourcepacks/cutebear_furniture.zip"
)
os.system(
    "cp ./cutebear_furniture.zip /home/cutebear/.local/share/PrismLauncher/instances/1.21.10/minecraft/resourcepacks"
)
os.system("rm -f /tmp/reloadpack")
os.system("touch /tmp/reloadpack")
