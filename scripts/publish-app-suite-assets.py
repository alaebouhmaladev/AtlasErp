"""Publish only the optional app bundle entries into the persistent asset map."""

import json
import shutil
from pathlib import Path

def publish(source, target, required):
    fresh = json.loads(source.read_text())
    current = json.loads(target.read_text()) if target.exists() else {}
    updates = {key: value for key, value in fresh.items()
               if value.startswith(("/assets/hrms/", "/assets/whatsapp/", "/assets/crm/"))}
    assert required <= updates.keys(), "Missing HR bundle build"
    backup = target.with_name(target.name + ".before-app-suite")
    if target.exists() and not backup.exists():
        shutil.copy2(target, backup)
    current.update(updates)
    temp = target.with_suffix(".app-suite.tmp")
    temp.write_text(json.dumps(current, indent=2))
    temp.replace(target)
    print(f"Published {len(updates)} optional entries in {target.name}; existing ERP/POS entries preserved")


publish(Path("app-suite-assets.json"), Path("sites/assets/assets.json"),
        {"hrms.bundle.js", "hrms.bundle.css"})
publish(Path("app-suite-assets-rtl.json"), Path("sites/assets/assets-rtl.json"),
        {"rtl_hrms.bundle.css"})
