"""Paladin's furniture beyond cutebear's first pieces, imported by tools/import_pfm.py.

Each item names the Paladin model its look comes from, the stonecutter inputs that make it, and how the plugin places
it. Angles are in the model, measured clockwise from +x seen from above (east 0, south 90, west 180, north 270):
`front` is the side that faces the player for floor pieces, `mount` the side against the wall for wall pieces.
Keep this list in step with what the CutebearFurniture plugin reads from furniture.json.
"""

COLOURS = [
    "white", "orange", "magenta", "light_blue", "yellow", "lime", "pink", "gray",
    "light_gray", "cyan", "purple", "blue", "brown", "green", "red", "black",
]

# Froggy chair colours, and the concrete each is cut from.
FROGGY = {"": "green", "pink": "pink", "light_blue": "light_blue", "blue": "blue", "orange": "orange", "yellow": "yellow"}

# Appliance finishes, their names and the block each is cut from.
FINISHES = {"white": ("White", "white_concrete"), "gray": ("Gray", "gray_concrete"), "iron": ("Iron", "iron_block")}


def title(text: str) -> str:
    return " ".join(word.capitalize() for word in text.split("_"))


def item(id, name, model, inputs, placement="floor", angle=0, seat=False, solid=True, light=0, height=1):
    return {"id": id, "name": name, "model": model, "inputs": inputs, "placement": placement, "angle": angle,
            "seat": seat, "solid": solid, "light": light, "height": height}


def items():
    for colour in COLOURS:
        yield item(f"{colour}_simple_sofa", f"Simple {title(colour)} Sofa", f"pfm:block/sofa_simple/{colour}/sofa_simple",
                   [f"{colour}_wool"], seat=True)
        yield item(f"{colour}_chair_classic", f"Classic {title(colour)} Oak Chair",
                   f"pfm:block/chair_classic/wool/{colour}/chair_classic", [f"{colour}_wool"], seat=True)
        yield item(f"{colour}_shower_towel", f"{title(colour)} Shower Towel",
                   f"pfm:block/shower_towel/{colour}_shower_towel", [f"{colour}_carpet"], "wall", 270, solid=False)
    for suffix, colour in FROGGY.items():
        id = "froggy_chair" + (f"_{suffix}" if suffix else "")
        name = (f"{title(suffix)} " if suffix else "") + "Froggy Chair"
        yield item(id, name, f"pfm:block/froggy_chair/{id}", [f"{colour}_concrete"], seat=True)
    yield item("arm_chair_leather", "Leather Armchair", "pfm:block/arm_chair_leather", ["leather"], seat=True)

    for finish, (name, block) in FINISHES.items():
        folder = "iron_fridge" if finish == "iron" else f"{finish}_fridge"
        fridge = "iron_fridge_single" if finish == "iron" else "fridge_single"
        freezer = "iron_freezer" if finish == "iron" else "freezer_single"
        yield item(f"{finish}_fridge", f"{name} Fridge", f"pfm:block/{folder}/{fridge}", [block], angle=270)
        yield item(f"{finish}_freezer", f"{name} Freezer", f"pfm:block/{folder}/{freezer}", [block], angle=270)
        yield item(f"{finish}_stove", f"{name} Stove", f"pfm:block/{finish}_stove", [block], angle=270)
        yield item(f"{finish}_oven_range_hood", f"{name} Oven Range Hood",
                   f"pfm:block/{finish}_oven_range_hood/{finish}_oven_range_hood", [block], "wall", 270, solid=False)
    yield item("xbox_fridge", "Xbox Series X Fridge", "pfm:block/xbox_fridge/xbox_fridge_full", ["black_concrete"],
               angle=270, height=2)
    yield item("iron_microwave", "Iron Microwave", "pfm:block/iron_microwave/iron_microwave", ["iron_block"],
               angle=270, solid=False)
    yield item("iron_toaster", "Iron Toaster", "pfm:block/iron_toaster/iron_toaster_off", ["iron_block"],
               angle=90, solid=False)
    yield item("kitchen_stovetop", "Kitchen Stovetop", "pfm:block/kitchen_counter/kitchen_stovetop", ["iron_block"],
               angle=270, solid=False)

    yield item("simple_light", "Simple Ceiling Light", "pfm:block/simple_light/simple_light", ["glowstone"],
               "ceiling", solid=False, light=15)
    for finish, block in (("white", "white_concrete"), ("gray", "gray_concrete"), ("glass", "glass")):
        yield item(f"{finish}_modern_pendant", f"{title(finish)} Modern Light Pendant",
                   f"pfm:block/{finish}_modern_pendant/{finish}_modern_pendant" if finish != "gray"
                   else "pfm:block/modern_pendant/modern_pendant", [block], "ceiling", solid=False, light=15)
    yield item("light_switch", "Light Switch", "pfm:block/light_switch/light_switch", ["lever"], "wall", 90, solid=False)
    yield item("white_mirror", "White Mirror", "pfm:block/mirror/mirror", ["glass_pane"], "wall", 270, solid=False)
    yield item("gray_mirror", "Gray Mirror", "pfm:block/gray_mirror/gray_mirror", ["glass_pane"], "wall", 270,
               solid=False)

    yield item("basic_plate", "Basic Plate", "pfm:block/basic_plate/basic_plate", ["bowl"], angle=180, solid=False)
    yield item("basic_cutlery", "Basic Cutlery", "pfm:block/basic_plate/cutlery", ["iron_nugget"], angle=180,
               solid=False)
    yield item("basic_shower_head", "Basic Shower Head", "pfm:block/shower/shower_head", ["iron_bars"], "wall", 90,
               solid=False)
    yield item("basic_shower_handle", "Basic Shower Handle", "pfm:block/shower/shower_handle", ["iron_bars"], "wall",
               90, solid=False)
    yield item("wall_toilet_paper", "Toilet Paper", "pfm:block/wall_toilet_paper/toilet_paper_wall", ["paper"], "wall",
               90, solid=False)
    yield item("mesh_trashcan", "Mesh Trashcan", "pfm:block/mesh_trashcan", ["iron_bars"], angle=270)
    yield item("working_table", "Furniture Workbench", "pfm:block/working_table", ["crafting_table"], angle=270)
