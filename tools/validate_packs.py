"""Check the built packs: every Java item resolves to a model and textures, every Bedrock attachable to a geometry and
texture, every Geyser mapping to an attachable and icon, and nothing in the last release changed or went missing.

Usage: python3 -I tools/validate_packs.py JAVA_ZIP MCPACK GEYSER_JSON CLIENT_JAR RELEASE_ZIP RELEASE_MCPACK RELEASE_JSON EXPECTED_ITEMS
"""

import json
import sys
import zipfile

java_zip, be_zip, geyser_json, vanilla_jar, release_zip, release_mcpack, release_json = sys.argv[1:8]
expected_items = int(sys.argv[8])
problems = []

java = zipfile.ZipFile(java_zip)
names = set(java.namelist())
vanilla = set(zipfile.ZipFile(vanilla_jar).namelist())
items = sorted(n.split("/")[-1][:-5] for n in names if n.startswith("assets/cutebear_furniture/items/") and n.endswith(".json"))
print(f"Java: {len(items)} item definitions, pack.mcmeta={'pack.mcmeta' in names}")
for item in items:
    definition = json.loads(java.read(f"assets/cutebear_furniture/items/{item}.json"))
    model_ref = definition["model"]["model"]
    model_path = f"assets/cutebear_furniture/models/{model_ref.split(':')[1]}.json"
    if model_path not in names:
        problems.append(f"{item}: missing model {model_path}")
        continue
    model = json.loads(java.read(model_path))
    textures = dict(model.get("textures", {}))
    if model.get("parent", "").startswith("cutebear_furniture:"):
        parent_path = f"assets/cutebear_furniture/models/{model['parent'].split(':')[1]}.json"
        if parent_path not in names:
            problems.append(f"{item}: missing parent {parent_path}")
            continue
        parent = json.loads(java.read(parent_path))
        textures = {**parent.get("textures", {}), **textures}
    for key, value in textures.items():
        if value.startswith("#"):
            continue
        namespace, _, texture = value.rpartition(":")
        path = f"assets/{namespace or 'minecraft'}/textures/{texture}.png"
        if path not in vanilla and path not in names:
            problems.append(f"{item}: texture {value} in neither the pack nor vanilla")

release = zipfile.ZipFile(release_zip)
for name in release.namelist():
    if name.endswith("/"):
        continue
    if name not in names:
        problems.append(f"Java: release file {name} missing")
    elif java.read(name) != release.read(name):
        problems.append(f"Java: {name} differs from release")

be = zipfile.ZipFile(be_zip)
be_names = set(be.namelist())
attachables = sorted(n for n in be_names if n.startswith("attachables/") and n.endswith(".json"))
geometries = {}
for n in be_names:
    if n.startswith("models/entity/") and n.endswith(".geo.json"):
        for geometry in json.loads(be.read(n))["minecraft:geometry"]:
            geometries[geometry["description"]["identifier"]] = n
item_texture = json.loads(be.read("textures/item_texture.json"))["texture_data"]
print(f"Bedrock: {len(attachables)} attachables, {len(geometries)} geometries, {len(item_texture)} item_texture entries, manifest={'manifest.json' in be_names}")
for n in attachables:
    description = json.loads(be.read(n))["minecraft:attachable"]["description"]
    geometry = description["geometry"]["default"]
    texture = description["textures"]["default"] + ".png"
    if geometry not in geometries:
        problems.append(f"{n}: geometry {geometry} missing")
    if texture not in be_names:
        problems.append(f"{n}: texture {texture} missing")
for key, value in item_texture.items():
    if value["textures"] + ".png" not in be_names:
        problems.append(f"item_texture {key}: {value['textures']} missing")

release_be = zipfile.ZipFile(release_mcpack)
for name in release_be.namelist():
    if name.endswith("/") or name in ("manifest.json", "textures/item_texture.json"):
        continue
    if name not in be_names:
        problems.append(f"Bedrock: release file {name} missing")
    elif be.read(name) != release_be.read(name):
        problems.append(f"Bedrock: {name} differs from release")

geyser = json.load(open(geyser_json))
entries = geyser["items"]["minecraft:poisonous_potato"]
models = [entry["model"] for entry in entries]
print(f"Geyser: {len(entries)} mappings, {len(set(models))} unique models")
release_entries = {e["model"]: e for e in json.load(open(release_json))["items"]["minecraft:poisonous_potato"]}
by_model = {e["model"]: e for e in entries}
for model, entry in release_entries.items():
    if by_model.get(model) != entry:
        problems.append(f"Geyser: {model} differs from release")
for entry in entries:
    identifier = entry["bedrock_identifier"].replace(":", ".")
    if identifier not in item_texture:
        problems.append(f"Geyser: {entry['model']} has no Bedrock icon")
    if f"attachables/{entry['model'].split(':')[1]}.json" not in be_names:
        problems.append(f"Geyser: {entry['model']} has no attachable")

for count, label in ((len(items), "Java items"), (len(attachables), "attachables"), (len(entries), "Geyser mappings")):
    if count != expected_items:
        problems.append(f"{label}: {count}, expected {expected_items}")

print("\n".join(problems) if problems else "All checks passed")
sys.exit(1 if problems else 0)
