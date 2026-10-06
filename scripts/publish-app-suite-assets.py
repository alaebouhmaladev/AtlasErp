"""Publish only the optional app bundle entries into the persistent asset map."""

import json
import shutil
from pathlib import Path

source = Path("app-suite-assets.json")
target = Path("sites/assets/assets.json")
fresh = json.loads(source.read_text())
current = json.loads(target.read_text()) if target.exists() else {}
updates = {key: value for key, value in fresh.items()
           if value.startswith(("/assets/hrms/", "/assets/whatsapp/", "/assets/crm/"))}
assert "hrms.bundle.js" in updates and "hrms.bundle.css" in updates, "Missing HR bundle build"
backup = target.with_name("assets.json.before-app-suite")
if target.exists() and not backup.exists():
    shutil.copy2(target, backup)
current.update(updates)
temp = target.with_suffix(".app-suite.tmp")
temp.write_text(json.dumps(current, indent=2))
temp.replace(target)
print(f"Published {len(updates)} optional app bundle entries; existing ERP/POS entries preserved")
