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


def item(id, name, model, inputs, placement="floor", angle=0, seat=False, solid=True, light=0, height=1, storage=0,
         bed=None, use=None, climb=False):
    """storage: chest slots (9, 27 or 54). bed: the bed colour a bed sleeps as. use: what right-clicking opens.
    climb: whether players climb the piece like a ladder."""
    return {"id": id, "name": name, "model": model, "inputs": inputs, "placement": placement, "angle": angle,
            "seat": seat, "solid": solid, "light": light, "height": height, "storage": storage, "bed": bed, "use": use,
            "climb": climb}


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
        yield item(f"{finish}_fridge", f"{name} Fridge", f"pfm:block/{folder}/{fridge}", [block], angle=270, storage=54)
        yield item(f"{finish}_freezer", f"{name} Freezer", f"pfm:block/{folder}/{freezer}", [block], angle=270,
                   storage=54)
        yield item(f"{finish}_stove", f"{name} Stove", f"pfm:block/{finish}_stove", [block], angle=270)
        yield item(f"{finish}_oven_range_hood", f"{name} Oven Range Hood",
                   f"pfm:block/{finish}_oven_range_hood/{finish}_oven_range_hood", [block], "wall", 270)
    yield item("xbox_fridge", "Xbox Series X Fridge", "pfm:block/xbox_fridge/xbox_fridge_full", ["black_concrete"],
               angle=270, height=2, storage=54)
    yield item("iron_microwave", "Iron Microwave", "pfm:block/iron_microwave/iron_microwave", ["iron_block"],
               angle=270)
    yield item("iron_toaster", "Iron Toaster", "pfm:block/iron_toaster/iron_toaster_off", ["iron_block"], angle=90)
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
    yield item("mesh_trashcan", "Mesh Trashcan", "pfm:block/mesh_trashcan", ["iron_bars"], angle=270, storage=27)
    yield item("working_table", "Furniture Workbench", "pfm:block/working_table", ["crafting_table"], angle=270,
               use="stonecutter")


# The woods the first pieces come in: name, planks, log, its top, stripped log, the item tag of its logs, and what
# Paladin calls a log of it. Stems stand in for logs in the nether woods.
WOODS = {
    "oak": ("Oak", "oak_planks", "oak_log", "oak_log_top", "stripped_oak_log", "oak_logs", "Log"),
    "spruce": ("Spruce", "spruce_planks", "spruce_log", "spruce_log_top", "stripped_spruce_log", "spruce_logs", "Log"),
    "birch": ("Birch", "birch_planks", "birch_log", "birch_log_top", "stripped_birch_log", "birch_logs", "Log"),
    "jungle": ("Jungle", "jungle_planks", "jungle_log", "jungle_log_top", "stripped_jungle_log", "jungle_logs", "Log"),
    "acacia": ("Acacia", "acacia_planks", "acacia_log", "acacia_log_top", "stripped_acacia_log", "acacia_logs", "Log"),
    "dark_oak": ("Dark Oak", "dark_oak_planks", "dark_oak_log", "dark_oak_log_top", "stripped_dark_oak_log",
                 "dark_oak_logs", "Log"),
    "mangrove": ("Mangrove", "mangrove_planks", "mangrove_log", "mangrove_log_top", "stripped_mangrove_log",
                 "mangrove_logs", "Log"),
    "cherry": ("Cherry", "cherry_planks", "cherry_log", "cherry_log_top", "stripped_cherry_log", "cherry_logs", "Log"),
    "pale_oak": ("Pale Oak", "pale_oak_planks", "pale_oak_log", "pale_oak_log_top", "stripped_pale_oak_log",
                 "pale_oak_logs", "Log"),
    "poplar": ("Poplar", "poplar_planks", "poplar_log", "poplar_log_top", "stripped_poplar_log", "poplar_logs", "Log"),
    "crimson": ("Crimson", "crimson_planks", "crimson_stem", "crimson_stem_top", "stripped_crimson_stem",
                "crimson_stems", "Stem"),
    "warped": ("Warped", "warped_planks", "warped_stem", "warped_stem_top", "stripped_warped_stem", "warped_stems",
               "Stem"),
}

# The colour Minecraft tints things of each dye colour with (its firework colour), which Paladin uses for lamp shades
# and office chairs.
DYES = {
    "white": 0xF0F0F0, "orange": 0xEB8844, "magenta": 0xC354CD, "light_blue": 0x6689D3, "yellow": 0xDECF2A,
    "lime": 0x41CD34, "pink": 0xD88198, "gray": 0x434343, "light_gray": 0xABABAB, "cyan": 0x287697,
    "purple": 0x7B2FBE, "blue": 0x253192, "brown": 0x51301A, "green": 0x3B511A, "red": 0xB3312C, "black": 0x1E1B1B,
}


def block(name: str) -> str:
    return f"minecraft:block/{name}"


def planks_and_log(wood: str) -> dict:
    _, planks, log, _, _, _, _ = WOODS[wood]
    return {block("oak_planks"): block(planks), block("oak_log"): block(log)}


def log_and_top(wood: str) -> dict:
    _, _, log, top, _, _, _ = WOODS[wood]
    return {block("oak_log"): block(log), block("oak_log_top"): block(top)}


def stripped_log(wood: str) -> dict:
    return {block("stripped_oak_log"): block(WOODS[wood][4])}


def face(texture: str, uv: list, rotation: int = 0) -> dict:
    return {"texture": texture, "uv": uv, "rotation": rotation} if rotation else {"texture": texture, "uv": uv}


# Paladin's mattresses used the bed entity texture, which Minecraft 26.1 split into one texture per face of the bed
# block. These are its mattress and pillow rebuilt on those textures for the red bed (beds are recoloured like the
# wood), laid out like Paladin's whole-bed frame: two blocks along x, the foot from x 0 and the headboard at x 32. A
# mattress side shows rows 7 to 10 of the side textures, the strip vanilla beds show.
MATTRESS = {
    "textures": {
        "head_up": block("red_bed_head_up"), "foot_up": block("red_bed_foot_up"),
        "head_east": block("red_bed_head_east"), "head_west": block("red_bed_head_west"),
        "foot_east": block("red_bed_foot_east"), "foot_west": block("red_bed_foot_west"),
        "foot_south": block("red_bed_foot_south"), "pillow": block("bed_head_north"),
    },
    "elements": [
        {"from": [3, 5, 0], "to": [16, 9, 16], "faces": {
            "up": face("#foot_up", [0, 0, 16, 13], 90),
            "north": face("#foot_west", [0, 7, 13, 10]),
            "south": face("#foot_east", [3, 7, 16, 10]),
            "west": face("#foot_south", [0, 7, 16, 10]),
        }},
        {"from": [16, 5, 0], "to": [29, 9, 16], "faces": {
            "up": face("#head_up", [0, 3, 16, 16], 90),
            "north": face("#head_west", [3, 7, 16, 10]),
            "south": face("#head_east", [0, 7, 13, 10]),
        }},
        {"from": [21, 9, 1], "to": [29, 10, 15], "faces": {
            "up": face("#head_up", [2, 1, 14, 7], 90),
            "north": face("#pillow", [1, 7, 9, 8]),
            "south": face("#pillow", [1, 7, 9, 8]),
            "west": face("#pillow", [1, 7, 15, 8]),
        }},
    ],
}


def bedding(wood: str, colour: str) -> dict:
    textures = {block("oak_planks"): block(WOODS[wood][1])}
    for part in ("head_up", "foot_up", "head_east", "head_west", "foot_east", "foot_west", "foot_south"):
        textures[block(f"red_bed_{part}")] = block(f"{colour}_bed_{part}")
    return textures


def variant(id, name, family, parts, substitutions, inputs, placement="floor", angle=0, seat=False, solid=True,
            light=0, height=1, length=1, storage=0, bed=None, use=None, climb=False):
    """A piece retextured from its family's template, which every variant shares a Bedrock geometry with."""
    entry = item(id, name, None, inputs, placement, angle, seat, solid, light, height, storage, bed, use, climb)
    entry.update({"family": family, "parts": parts, "substitutions": substitutions, "length": length})
    return entry


# Wooden families: Paladin's part models for one free-standing piece, its name with the wood as {wood} and its log
# as {log}, how the wood is swapped in, and how the plugin places it.
WOODEN = [
    ("table_basic", "Basic {wood} Table", ["table_basic/table_basic"], planks_and_log, {}),
    ("table_classic", "Classic {wood} Table", ["table_classic/table_classic"], planks_and_log, {}),
    ("log_table", "{wood} {log} Table", ["log_table/log_table"], planks_and_log, {}),
    ("table_modern_dinner", "{wood} Modern Dining Table", ["table_modern_dinner/table_modern_dinner"],
     planks_and_log, {}),
    ("coffee_table_classic", "Classic {wood} Coffee Table", ["coffee_table_classic/coffee_table_classic"],
     planks_and_log, {}),
    ("coffee_table_modern", "Modern {wood} Coffee Table", ["coffee_table_modern/coffee_table_modern"],
     planks_and_log, {}),
    ("desk_basic", "Basic {wood} Desk",
     ["basic_desk/basic_desk_base", "basic_desk/basic_desk_north_east", "basic_desk/basic_desk_north_west",
      "basic_desk/basic_desk_south_east", "basic_desk/basic_desk_south_west"], planks_and_log, {}),
    ("desk_cabinet_basic", "Basic {wood} Desk Cabinet",
     ["basic_desk_cabinet/basic_desk_cabinet_closed", "basic_desk_cabinet/basic_desk_cabinet_leg_north_east",
      "basic_desk_cabinet/basic_desk_cabinet_leg_north_west", "basic_desk_cabinet/basic_desk_cabinet_leg_south_east",
      "basic_desk_cabinet/basic_desk_cabinet_leg_south_west"], planks_and_log, {"angle": 270, "storage": 27}),
    ("desk_cabinet_classic", "Classic {wood} Desk Cabinet", ["classic_desk/classic_desk_cabinet_all"],
     planks_and_log, {"angle": 90, "storage": 27}),
    ("classic_nightstand", "{wood} Classic Nightstand", ["classic_nightstand/classic_nightstand"], planks_and_log,
     {"angle": 180, "storage": 9}),
    ("log_stool", "{wood} {log} Stool", ["log_stool/log_stool"], log_and_top, {"seat": True}),
    ("simple_stool", "{wood} Simple Stool", ["simple_stool/simple_stool"], planks_and_log, {"seat": True}),
    ("modern_stool", "{wood} Modern Stool", ["modern_stool/modern_stool"], planks_and_log, {"seat": True}),
    ("kitchen_counter", "{wood} Kitchen Counter", ["kitchen_counter/kitchen_counter"], planks_and_log,
     {"angle": 90, "storage": 27}),
    ("kitchen_drawer", "{wood} Kitchen Drawer", ["kitchen_drawer/kitchen_drawer"], planks_and_log,
     {"angle": 90, "storage": 27}),
    ("kitchen_sink", "{wood} Kitchen Sink", ["kitchen_sink/kitchen_sink"], planks_and_log,
     {"angle": 90, "storage": 27}),
    ("kitchen_counter_oven", "{wood} Kitchen Oven", ["kitchen_counter_oven/kitchen_counter_oven"], planks_and_log,
     {"angle": 90}),
    ("kitchen_cabinet", "{wood} Wall Cabinet", ["kitchen_cabinet/kitchen_cabinet"], planks_and_log,
     {"placement": "wall", "angle": 270, "storage": 27}),
    ("kitchen_wall_counter", "{wood} Kitchen Filler Cabinet", ["kitchen_counter/kitchen_counter_middle"],
     planks_and_log, {"placement": "wall", "angle": 270, "storage": 27}),
    ("kitchen_wall_drawer", "{wood} Kitchen Cabinet", ["kitchen_drawer/kitchen_drawer_middle"], planks_and_log,
     {"placement": "wall", "angle": 270, "storage": 27}),
    ("kitchen_wall_small_drawer", "{wood} Kitchen Small Cabinet", ["kitchen_wall_drawer_small/kitchen_wall_drawer_small"],
     planks_and_log, {"placement": "wall", "angle": 270, "storage": 9}),
    ("simple_bunk_ladder", "{wood} Simple Bunk Ladder", ["simple_bunk_ladder/simple_ladder"], planks_and_log,
     {"placement": "wall", "angle": 90, "solid": False, "climb": True}),
]


# Cutebear's own wooden pieces, which are Paladin's models: the plugin already makes them in each wood, so these
# families only add their stripped and stone versions. Their names follow the plugin's.
ORIGINAL = [
    ("chair", "{wood} Chair", ["chair/chair"], {"seat": True}),
    ("chair_dinner", "{wood} Dinner Chair", ["chair_dinner/chair_dinner"], {"seat": True}),
    ("chair_classic", "{wood} Classic Chair", ["chair_classic/chair_classic"], {"seat": True}),
    ("chair_modern", "{wood} Modern Chair", ["chair_modern/chair_modern"], {"seat": True}),
    ("dinner_table", "{wood} Dinner Table", ["dinner_table/dinner_table"], {}),
    ("coffee_table_basic", "{wood} Coffee Table", ["coffee_table_basic/coffee_table_basic"], {}),
    ("classic_desk_all", "{wood} Classic Desk", ["classic_desk/classic_desk_all"], {}),
    ("classic_stool", "{wood} Classic Stool", ["classic_stool/classic_stool"], {"seat": True}),
]

# Wooden families Paladin makes only from logs.
LOG_ONLY = ("log_stool", "simple_bunk_ladder")

# Paladin's stone types: name, polished block and raw block. The polished block's texture takes the planks' place and
# the raw block's the logs', and pieces are cut from the polished block. Paladin finds one for every polished block
# that has a raw block, which on 26.3 includes cinnabar and sulfur, and adds calcite, quartz, netherite and the
# quartz-topped light and dark woods by hand.
STONES = {
    "stone": ("Stone", "stone", "cobblestone"),
    "granite": ("Granite", "polished_granite", "granite"),
    "diorite": ("Diorite", "polished_diorite", "diorite"),
    "andesite": ("Andesite", "polished_andesite", "andesite"),
    "deepslate": ("Deepslate", "polished_deepslate", "deepslate"),
    "blackstone": ("Blackstone", "polished_blackstone", "blackstone"),
    "basalt": ("Basalt", "polished_basalt", "basalt"),
    "tuff": ("Tuff", "polished_tuff", "tuff"),
    "cinnabar": ("Cinnabar", "polished_cinnabar", "cinnabar"),
    "sulfur": ("Sulfur", "polished_sulfur", "sulfur"),
    "calcite": ("Calcite", "calcite", "stripped_warped_stem"),
    "light_wood": ("Light Wood", "quartz_block", "stripped_oak_log"),
    "dark_wood": ("Dark Wood", "quartz_block", "stripped_dark_oak_log"),
    "quartz": ("Quartz", "quartz_block", "quartz_block"),
    "netherite": ("Netherite", "netherite_block", "ancient_debris"),
}

# Paladin's two-material kitchens and modern stools: name, the block whose texture takes the planks' place, the one
# that takes the logs' place, and the block a piece is cut from. Paladin's raw concrete fills the gaps it leaves.
COUNTERS = {
    "dark_concrete": ("Dark Concrete", "gray_concrete", "white_concrete", "gray_concrete"),
    "concrete": ("Concrete", "white_concrete", None, "white_concrete"),
    "smooth_stone": ("Smooth Stone", "white_concrete", "smooth_stone", "smooth_stone"),
    "deepslate_tile": ("Deepslate Tile", "quartz_block", "deepslate_tiles", "deepslate_tiles"),
    "granite_terracotta": ("Granite Terracotta", "white_terracotta", "polished_granite", "white_terracotta"),
    "andesite_oak": ("Andesite Stripped Oak", "stripped_oak_log", "polished_andesite", "polished_andesite"),
    "deepslate_dark_oak": ("Deepslate Dark Oak", "dark_oak_planks", "polished_deepslate", "polished_deepslate"),
    "blackstone_crimson": ("Blackstone Crimson", "crimson_planks", "polished_blackstone", "polished_blackstone"),
}
STOOLS = {
    "gray_dark_oak": ("Gray Dark Oak", "gray_concrete", "stripped_dark_oak_log", "gray_concrete"),
    "white": ("White", "white_concrete", "light_gray_concrete", "white_concrete"),
    "gray": ("Gray", None, "light_gray_concrete", "gray_concrete"),
    "light_gray_dark_oak": ("Light Gray Dark Oak", "light_gray_concrete", "stripped_dark_oak_log",
                            "light_gray_concrete"),
}

# Paladin takes the texture a block shows on its north side.
SIDES = {"quartz_block": "quartz_block_side", "basalt": "basalt_side", "polished_basalt": "polished_basalt_side",
         "ancient_debris": "ancient_debris_side"}


def side(name: str | None) -> str:
    return "pfm:block/raw_concrete" if name is None else block(SIDES.get(name, name))


def materials(planks: str, log: str) -> dict:
    return {block("oak_planks"): planks, block("oak_log"): log}


def stripped(wood: str) -> dict:
    """Paladin's stripped pieces put the stripped log where the planks were and the planks where the log was."""
    _, planks, _, _, stripped_log, _, _ = WOODS[wood]
    return materials(block(stripped_log), block(planks))


def raw(wood: str, strip: bool) -> dict:
    """The raw log table is all log, stripped or not."""
    log = block(WOODS[wood][4 if strip else 2])
    return materials(log, log)


def stone(name: str, kitchen: bool) -> dict:
    _, polished, raw_block = STONES[name]
    top, bottom = side(polished), side(raw_block)
    if kitchen and name in ("calcite", "netherite"):
        # Paladin's kitchens swap these two, so the raw block forms the cabinet.
        top, bottom = bottom, top
    return materials(top, bottom)


def stripped_inputs(wood: str) -> list:
    log = WOODS[wood][4]
    return [log, log.replace("_log", "_wood").replace("_stem", "_hyphae")]


def other_materials(family: str, name: str, models: list, options: dict):
    """A wooden family's stripped and stone versions, and Paladin's two-material kitchens and stools."""
    kitchen = family.startswith("kitchen_")
    for wood, (wood_name, _, _, _, _, _, log) in WOODS.items():
        yield variant(f"stripped_{wood}_{family}", name.format(wood=f"Stripped {wood_name}", log=log), family, models,
                      stripped(wood), stripped_inputs(wood), **options)
    if family == "log_table":
        for wood, (wood_name, _, _, _, _, tag, log) in WOODS.items():
            yield variant(f"{wood}_raw_log_table", f"Raw {wood_name} {log} Table", family, models, raw(wood, False),
                          [f"#{tag}"], **options)
            yield variant(f"stripped_{wood}_raw_log_table", f"Raw Stripped {wood_name} {log} Table", family, models,
                          raw(wood, True), stripped_inputs(wood), **options)
    for key, (stone_name, polished, _) in STONES.items():
        if kitchen and key == "quartz":
            continue  # Paladin makes no quartz kitchens: Deepslate Tile is its quartz counter.
        id = f"{key}_natural_table" if family == "log_table" else f"{key}_{family}"
        yield variant(id, name.format(wood=stone_name, log="Natural"), family, models, stone(key, kitchen), [polished],
                      **options)
    extras = COUNTERS if kitchen else STOOLS if family == "modern_stool" else {}
    for key, (extra_name, planks, log, cut_from) in extras.items():
        yield variant(f"{key}_{family}", name.format(wood=extra_name, log=""), family, models,
                      materials(side(planks), side(log)), [cut_from], **options)


def family_items():
    """Paladin's furniture that comes in each wood, and in each colour: the pieces whose looks share a template."""
    for family, name, parts, swap, options in WOODEN:
        models = [f"pfm:block/{part}" for part in parts]
        for wood, (wood_name, _, _, _, _, tag, log) in WOODS.items():
            yield variant(f"{wood}_{family}", name.format(wood=wood_name, log=log), family, models, swap(wood),
                          [f"#{tag}"], **options)
        if family not in LOG_ONLY:
            yield from other_materials(family, name, models, options)
    for family, name, parts, options in ORIGINAL:
        yield from other_materials(family, name, [f"pfm:block/{part}" for part in parts], options)
    for style in ("simple", "classic"):
        parts = [f"pfm:block/{style}_bed/template/full/{style}_bed", MATTRESS]
        for wood, (wood_name, *_) in WOODS.items():
            for colour in COLOURS:
                yield variant(f"{wood}_{colour}_{style}_bed", f"{wood_name} {title(colour)} {title(style)} Bed",
                              f"{style}_bed", parts, bedding(wood, colour), [f"{colour}_bed"], angle=180, length=2,
                              bed=colour)
    lamp = ["pfm:block/basic_lamp/basic_lamp_single", "pfm:block/basic_lamp/basic_lamp_shade",
            "pfm:block/basic_lamp/basic_lamp_light_bulb_on"]
    for wood, (wood_name, *_) in WOODS.items():
        for colour in COLOURS:
            yield variant(f"basic_{colour}_{wood}_lamp", f"Basic {title(colour)} {wood_name} Lamp", "basic_lamp", lamp,
                          {**stripped_log(wood), "pfm:block/lamp_shade": ("tint", DYES[colour], colour)},
                          [f"{colour}_wool"], light=15)
    chair = ["pfm:block/office_chair/office_chair"]
    for colour in COLOURS:
        tint = ("tint", DYES[colour], colour)
        yield variant(f"{colour}_office_chair", f"{title(colour)} Office Chair", "office_chair", chair,
                      {"pfm:block/office_chair/office_chair_back": tint, "pfm:block/office_chair/office_chair_seat": tint},
                      [f"{colour}_wool"], angle=270, seat=True)
