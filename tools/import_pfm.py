"""Import the furniture in pfm_items.py from Paladin's Furniture into resources/pfm/.

Usage: python3 -I tools/import_pfm.py PFM_ASSETS_DIR CLIENT_JAR

PFM_ASSETS_DIR is common/src/main/resources/assets/pfm from Paladin's Furniture at commit 01ec5d7, the last one before
its models and textures moved from LGPL-3.0 to the PolyForm Shield licence. CLIENT_JAR is a Minecraft client jar for
the vanilla textures the models use. Writes, for each item, the Java model (models/), the Bedrock geometry and atlas
(bedrock/), the Paladin textures the Java models need (textures/), and furniture.json, which the plugin reads.

A family (the pieces that come in each wood or colour) gets one template: a Java model in models/pfm/ that each
piece's model retextures, and a Bedrock geometry that each piece's atlas fits. geometry.json names it for each piece.
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from pfm import NAMESPACE, Sources, bake, bake_family, compose, flatten, java_model, retexture  # noqa: E402
from pfm_items import family_items, items  # noqa: E402

OUT = ROOT / "resources" / "pfm"


def yaw_offset(entry: dict) -> int:
    """Degrees the plugin adds to the yaw it starts from: the player's facing (floor, ceiling) or the wall's (wall).

    An item display shows its model turned half a turn, so model +x points west at yaw 0; a model direction at angle a
    ends up at world angle yaw + 180 + a.
    """
    if entry["placement"] == "floor":
        return (-entry["angle"]) % 360
    if entry["placement"] == "wall":
        return (-180 - entry["angle"]) % 360
    return 0


def entry_for(entry: dict, length: int = 1) -> dict:
    """What furniture.json says about an item."""
    footprint = [[x, y, 0] for x in range(length) for y in range(entry["height"])] if entry["solid"] else []
    return {
        "id": entry["id"],
        "name": entry["name"],
        "inputs": entry["inputs"],
        "placement": entry["placement"],
        "yaw_offset": yaw_offset(entry),
        "seat": entry["seat"],
        "light": entry["light"],
        "footprint": footprint,
    }


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent="\t") + "\n")


def main() -> None:
    sources = Sources(Path(sys.argv[1]), Path(sys.argv[2]))
    if OUT.exists():
        shutil.rmtree(OUT)
    for folder in ("models/pfm", "bedrock", "textures"):
        (OUT / folder).mkdir(parents=True)
    registry, needed, geometries = [], set(), {}
    for entry in items():
        model = flatten(sources, entry["model"])
        java, textures = java_model(model)
        needed |= textures
        write_json(OUT / "models" / f"{entry['id']}.json", java)
        geometry, atlas = bake(sources, model, entry["id"])
        write_json(OUT / "bedrock" / f"{entry['id']}.geo.json", geometry)
        atlas.save(OUT / "bedrock" / f"{entry['id']}.png", optimize=True)
        registry.append(entry_for(entry))
    families = {}
    for entry in family_items():
        families.setdefault(entry["family"], []).append(entry)
    for family, entries in families.items():
        template = compose(sources, entries[0]["parts"])
        base, textures = java_model(template)
        needed |= textures
        write_json(OUT / "models" / "pfm" / f"{family}.json", base)
        variants = {entry["id"]: retexture(sources, template, entry["substitutions"]) for entry in entries}
        geometry, atlases = bake_family(sources, template, variants, f"pfm_{family}")
        write_json(OUT / "bedrock" / f"pfm_{family}.geo.json", geometry)
        for entry in entries:
            java, textures = java_model(variants[entry["id"]])
            needed |= textures
            changed = {key: value for key, value in java["textures"].items() if base["textures"].get(key) != value}
            write_json(OUT / "models" / f"{entry['id']}.json",
                       {"parent": f"{NAMESPACE}:pfm/{family}", "textures": changed} if changed
                       else {"parent": f"{NAMESPACE}:pfm/{family}"})
            atlases[entry["id"]].save(OUT / "bedrock" / f"{entry['id']}.png", optimize=True)
            geometries[entry["id"]] = f"pfm_{family}"
            registry.append(entry_for(entry, entry["length"]))
    for reference in sorted(needed):
        path = reference.split(":", 1)[1].removeprefix("block/")
        target = OUT / "textures" / f"{path}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(sources.texture_bytes(reference))
    write_json(OUT / "furniture.json", {"items": registry})
    write_json(OUT / "geometry.json", geometries)
    print(f"{len(registry)} items, {len(families)} families, {len(needed)} textures written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
