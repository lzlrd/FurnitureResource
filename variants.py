"""Wood, wool, concrete and gold variants of the furniture.

Keep this list in sync with the recipes in the CutebearFurniture plugin.
Existing item IDs (oak furniture, white_arm_chair, trash_can, the quartz
bathroom) stay unchanged so furniture that is already placed keeps working.
"""

# Wood type: (planks texture, log texture).
WOODS = {
    "oak": ("oak_planks", "oak_log"),
    "spruce": ("spruce_planks", "spruce_log"),
    "birch": ("birch_planks", "birch_log"),
    "jungle": ("jungle_planks", "jungle_log"),
    "acacia": ("acacia_planks", "acacia_log"),
    "dark_oak": ("dark_oak_planks", "dark_oak_log"),
    "mangrove": ("mangrove_planks", "mangrove_log"),
    "cherry": ("cherry_planks", "cherry_log"),
    "pale_oak": ("pale_oak_planks", "pale_oak_log"),
    "poplar": ("poplar_planks", "poplar_log"),
    "crimson": ("crimson_planks", "crimson_stem"),
    "warped": ("warped_planks", "warped_stem"),
}

WOODEN_FURNITURE = [
    "chair",
    "dinner_table",
    "coffee_table_basic",
    "classic_desk_all",
    "classic_stool",
    "chair_classic",
    "chair_modern",
    "chair_dinner",
]

QUARTZ_FURNITURE = [
    "bathtub",
    "basic_sink",
    "toilet",
]

# The quartz parts of the bathroom furniture become gold; fittings keep their texture.
GOLD = {
    "quartz_block_bottom": "gold_block",
    "quartz_block_side": "gold_block",
    "quartz_block_top": "gold_block",
}

COLOURS = [
    "white",
    "orange",
    "magenta",
    "light_blue",
    "yellow",
    "lime",
    "pink",
    "gray",
    "light_gray",
    "cyan",
    "purple",
    "blue",
    "brown",
    "green",
    "red",
    "black",
]


def variants():
    """Yield (item ID, base model, {vanilla texture: replacement texture})."""
    for wood, (planks, log) in WOODS.items():
        if wood == "oak":
            continue
        for base in WOODEN_FURNITURE:
            yield f"{wood}_{base}", base, {"oak_planks": planks, "oak_log": log}
    for colour in COLOURS:
        if colour != "white":
            yield f"{colour}_arm_chair", "white_arm_chair", {"white_wool": f"{colour}_wool"}
    for colour in COLOURS:
        if colour != "gray":
            yield f"{colour}_trash_can", "trash_can", {"gray_concrete": f"{colour}_concrete"}
    for base in QUARTZ_FURNITURE:
        yield f"gold_{base}", base, GOLD
