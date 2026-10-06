"""Explicit public demonstration catalog, never an unfiltered ERP item query."""
import json
from pathlib import Path
import frappe

sitemap = 0


def get_context(context):
    data = json.loads(Path(frappe.get_app_path("atlas_erp", "public", "data", "streetpizza-menu.json")).read_text())
    context.title = "Street Pizza · ATLASERP"
    context.business = data["business"]
    groups = {}
    for item in data["items"]:
        groups.setdefault(item["category"], []).append(item)
    # Avoid context.items: that collides with dict.items in Jinja.
    context.menu_groups = [{"name": name, "entries": entries} for name, entries in groups.items()]
    context.menu_count = len(data["items"])
    context.source_date = data["captured_on"]
    return context
