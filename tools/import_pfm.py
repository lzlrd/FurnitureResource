"""Import the furniture in pfm_items.py from Paladin's Furniture into resources/pfm/.

Usage: python3 -I tools/import_pfm.py PFM_ASSETS_DIR CLIENT_JAR

PFM_ASSETS_DIR is common/src/main/resources/assets/pfm from Paladin's Furniture at commit 01ec5d7, the last one before
its models and textures moved from LGPL-3.0 to the PolyForm Shield licence. CLIENT_JAR is a Minecraft client jar for
the vanilla textures the models use. Writes, for each item, the Java model (models/), the Bedrock geometry and atlas
(bedrock/), the Paladin textures the Java models need (textures/), and furniture.json, which the plugin reads.
"""

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from pfm import Sources, bake, flatten, java_model  # noqa: E402
from pfm_items import items  # noqa: E402

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


def main() -> None:
    sources = Sources(Path(sys.argv[1]), Path(sys.argv[2]))
    if OUT.exists():
        shutil.rmtree(OUT)
    for folder in ("models", "bedrock", "textures"):
        (OUT / folder).mkdir(parents=True)
    registry, needed = [], set()
    for entry in items():
        model = flatten(sources, entry["model"])
        java, textures = java_model(model)
        needed |= textures
        (OUT / "models" / f"{entry['id']}.json").write_text(json.dumps(java, indent="\t") + "\n")
        geometry, atlas = bake(sources, model, entry["id"])
        (OUT / "bedrock" / f"{entry['id']}.geo.json").write_text(json.dumps(geometry, indent="\t") + "\n")
        atlas.save(OUT / "bedrock" / f"{entry['id']}.png", optimize=True)
        footprint = [[0, y, 0] for y in range(entry["height"])] if entry["solid"] else []
        registry.append({
            "id": entry["id"],
            "name": entry["name"],
            "inputs": entry["inputs"],
            "placement": entry["placement"],
            "yaw_offset": yaw_offset(entry),
            "seat": entry["seat"],
            "light": entry["light"],
            "footprint": footprint,
        })
    for reference in sorted(needed):
        path = reference.split(":", 1)[1].removeprefix("block/")
        target = OUT / "textures" / f"{path}.png"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(sources.texture_bytes(reference))
    (OUT / "furniture.json").write_text(json.dumps({"items": registry}, indent="\t") + "\n")
    print(f"{len(registry)} items, {len(needed)} Paladin textures written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
