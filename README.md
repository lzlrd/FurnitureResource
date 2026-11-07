# Resource Pack builder for cutebear's furniture

## All models come from [paladins-furniture](https://github.com/UnlikePaladin/paladins-furniture)

Fork of [cutebear/FurnitureResource](https://codeberg.org/cutebear/FurnitureResource) that adds wood, wool, concrete and gold variants and 941 more pieces from Paladin's Furniture for the [CutebearFurniture fork](https://github.com/lzlrd/CutebearFurniture).

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

## Pieces from Paladin's Furniture

`resources/pfm` holds sofas, chairs, tables, desks, stools, kitchens, beds, lamps, lights, bathroom fittings and more, converted from Paladin's Furniture at commit 01ec5d7, the last before its assets left the LGPL (see [NOTICE.md](NOTICE.md)). `pfm_items.py` lists them: the Paladin model each comes from, its stonecutter inputs, and how the plugin places it.

The pieces that come in each wood, and the beds, lamps and office chairs that come in each colour, are families: one template model, put together from Paladin's parts for a free-standing piece, retextured for each variant as Paladin does at run time. Java gets the template in `models/pfm/` and a small model per piece that swaps its textures; Bedrock gets one geometry per family and an atlas per piece. Lamp shades and office chairs are tinted with the dye's colour. Minecraft 26.1 split the bed entity texture Paladin's mattresses used into one texture per face of the bed block, so `pfm_items.py` rebuilds the mattress on those.

After changing `pfm_items.py`, check out that commit of [Paladin's Furniture](https://github.com/UnlikePaladin/paladins-furniture) and import again:

```sh
python3 -I tools/import_pfm.py path/to/paladins-furniture/common/src/main/resources/assets/pfm path/to/client.jar
```

It merges each Java model's parents, copies the Paladin textures it uses, bakes Bedrock geometry and a texture atlas, and writes `resources/pfm/furniture.json`. Copy that file to the plugin's `src/main/resources`: the plugin reads it for each piece's recipe, placement, seat, light and barriers.

To check a build against the last release, with the release's three files and a client jar:

```sh
python3 -I tools/validate_packs.py cutebear_furniture.zip cutebear_furniture.mcpack cutebear_furniture.json path/to/client.jar release.zip release.mcpack release.json 219
```

The last argument is the number of items the build should have.
