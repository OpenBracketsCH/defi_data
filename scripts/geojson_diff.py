import json
import sys

old_file = sys.argv[1]
new_file = sys.argv[2]

def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

old = load(old_file)
new = load(new_file)

def index(features):
    return {
        f["properties"].get("id"): f
        for f in features
        if "id" in f.get("properties", {})
    }

old_idx = index(old["features"])
new_idx = index(new["features"])

added = new_idx.keys() - old_idx.keys()
removed = old_idx.keys() - new_idx.keys()
common = new_idx.keys() & old_idx.keys()

out = []

out.append("🆕 NEUE EINTRÄGE")
out.append("=" * 30)
if not added:
    out.append("Keine")
for i in added:
    p = new_idx[i]["properties"]
    out.append(f"- {p.get('name','(ohne Name)')} (ID: {i})")

out.append("\n❌ ENTFERNTE EINTRÄGE")
out.append("=" * 30)
if not removed:
    out.append("Keine")
for i in removed:
    p = old_idx[i]["properties"]
    out.append(f"- {p.get('name','(ohne Name)')} (ID: {i})")

out.append("\n✏️ GEÄNDERTE EINTRÄGE")
out.append("=" * 30)
found = False
for i in common:
    old_p = old_idx[i]["properties"]
    new_p = new_idx[i]["properties"]

    changes = []
    for k in new_p:
        if old_p.get(k) != new_p.get(k):
            changes.append(
                f"  • {k}: '{old_p.get(k)}' → '{new_p.get(k)}'"
            )

    if changes:
        found = True
        out.append(f"- {new_p.get('name','(ohne Name)')} (ID: {i})")
        out.extend(changes)

if not found:
    out.append("Keine")

print("\n".join(out))
