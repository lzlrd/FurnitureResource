"""Generate the Bedrock textures for every variant in variants.py.

Usage:
    python3 tools/generate_variant_textures.py [CLIENT_JAR]

Without CLIENT_JAR, the latest release client jar is downloaded from Mojang.
Writes resources/customModel/variants/<item>.png.
"""

import io
import json
import sys
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from remap import build_mapping, render  # noqa: E402
from variants import variants  # noqa: E402

MODELS = ROOT / "resources" / "customModel"
OUTPUT = MODELS / "variants"
MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"


def latest_client_jar() -> bytes:
    with urllib.request.urlopen(MANIFEST) as response:
        manifest = json.load(response)
    release = manifest["latest"]["release"]
    version_url = next(v["url"] for v in manifest["versions"] if v["id"] == release)
    with urllib.request.urlopen(version_url) as response:
        client_url = json.load(response)["downloads"]["client"]["url"]
    print(f"Downloading the {release} client jar")
    with urllib.request.urlopen(client_url) as response:
        return response.read()


def main() -> None:
    jar_bytes = Path(sys.argv[1]).read_bytes() if len(sys.argv) > 1 else latest_client_jar()
    jar = zipfile.ZipFile(io.BytesIO(jar_bytes))
    cache: dict[str, np.ndarray] = {}

    def load(name: str) -> np.ndarray:
        if name not in cache:
            data = jar.read(f"assets/minecraft/textures/block/{name}.png")
            cache[name] = np.asarray(Image.open(io.BytesIO(data)).convert("RGBA"))
        return cache[name]

    OUTPUT.mkdir(exist_ok=True)
    mappings = {}
    for item, parent, substitutions in variants():
        if parent not in mappings:
            atlas = np.asarray(Image.open(MODELS / f"{parent}.png").convert("RGBA"))
            mappings[parent] = build_mapping(MODELS, parent, atlas, load)
            mapping = mappings[parent]
            print(f"{parent}: traced {mapping['mapped']}/{mapping['opaque']} pixels to vanilla textures")
        Image.fromarray(render(mappings[parent], load, substitutions)).save(OUTPUT / f"{item}.png", optimize=True)
    print(f"Wrote {sum(1 for _ in variants())} textures to {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
