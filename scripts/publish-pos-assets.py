"""Publish the image's POS bundle hash into the persistent sites asset manifest.

Run from the bench directory after starting the matching backend/frontend images,
then run bench --site SITE clear-cache. Other app bundle hashes are preserved.
"""
import json
from pathlib import Path


def main():
    key = "point-of-sale.bundle.js"
    source = json.loads(Path("pos-assets.json").read_text())
    value = source[key]
    if not value.startswith("/assets/erpnext/dist/js/point-of-sale.bundle."):
        raise SystemExit("Unexpected POS asset path")
    if not Path("sites" + value).is_file():
        raise SystemExit("POS asset is missing from the running image")
    target = Path("sites/assets/assets.json")
    current = json.loads(target.read_text())
    if current.get(key) != value:
        backup = target.with_name("assets.json.before-pos-repair")
        if not backup.exists():
            backup.write_bytes(target.read_bytes())
        current[key] = value
        temporary = target.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(current, indent=4) + "\n")
        temporary.replace(target)
    print("POS asset registered:", value)


if __name__ == "__main__":
    main()
