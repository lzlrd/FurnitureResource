# Resource Pack builder for cutebear's furniture

## All models come from [paladins-furniture](https://github.com/UnlikePaladin/paladins-furniture)

Fork of [cutebear/FurnitureResource](https://codeberg.org/cutebear/FurnitureResource) that adds wood, wool, concrete and gold variants for the [CutebearFurniture fork](https://github.com/lzlrd/CutebearFurniture).

## Build

Prebuilt files are on the [Releases](https://github.com/lzlrd/FurnitureResource/releases) page. To build them yourself:

```sh
git clone --recurse-submodules https://github.com/lzlrd/FurnitureResource.git
cd FurnitureResource
python3 main.py
```

Needs Python 3.12+, Pillow and 7-Zip (`7z`). Outputs `cutebear_furniture.zip` (Java resource pack), `cutebear_furniture.mcpack` (Bedrock pack for Geyser's `packs` folder) and `cutebear_furniture.json` (Geyser's `custom_mappings` folder).

## Variants

`variants.py` lists the variants: every wooden piece in each wood type, the arm chair in each wool colour, the trash can in each concrete colour, and the bathtub, sink and toilet in gold. Java models inherit the base model and swap textures. Bedrock textures are rebuilt from the baked base textures with the matching vanilla textures.

After changing `variants.py`, regenerate the Bedrock textures, then build:

```sh
pip install numpy pillow
python3 tools/generate_variant_textures.py [path/to/client.jar]
```

Without a jar it downloads the latest release client jar from Mojang. Keep `variants.py` in sync with the recipes in the plugin.
