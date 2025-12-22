import json
from pathlib import Path


def write_wallet(user_context: dict, org_id: str):
    Path("output").mkdir(exist_ok=True)
    path = Path("output") / f"{org_id}_user_context.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(user_context, f, indent=2)

    return path
