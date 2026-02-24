"""
One-off standalone utility:
Copy tag names from Contact tags + Sales tags into Project/Task tags (project.tags).

Default mode is DRY RUN (no writes). Use --apply to create missing tags.

Output report:
- 3_Documentation/Project_Task_Tag_Seed_Report.csv
"""

import argparse
import csv
import sys
from typing import Any, Dict, List, Set, Tuple

import json
from urllib import request

ODOO_URL = "https://window-solar-care.odoo.com/jsonrpc"
ODOO_DB = "window-solar-care"
ODOO_USER_ID = 2
ODOO_API_KEY = "7e92006fd5c71e4fab97261d834f2e6004b61dc6"

REPORT_PATH = "3_Documentation/Project_Task_Tag_Seed_Report.csv"


def odoo_execute(model: str, method: str, args: List[Any], kwargs: Dict[str, Any] | None = None) -> Any:
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [ODOO_DB, ODOO_USER_ID, ODOO_API_KEY, model, method, args, kwargs or {}],
        },
    }
    req = request.Request(ODOO_URL, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    with request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
    data = json.loads(raw)
    if data.get("error"):
        raise RuntimeError(f"Odoo error on {model}.{method}: {data['error']}")
    return data.get("result")


def model_exists(model: str) -> bool:
    ids = odoo_execute("ir.model", "search", [[["model", "=", model]]], {"limit": 1})
    return bool(ids)


def read_tags(model: str) -> List[Dict[str, Any]]:
    return odoo_execute(model, "search_read", [[]], {"fields": ["id", "name"], "limit": 5000})


def create_project_tag(name: str) -> int:
    new_id = odoo_execute("project.tags", "create", [{"name": name}], {})
    if not isinstance(new_id, int):
        raise RuntimeError(f"Unexpected create result for tag '{name}': {new_id}")
    return new_id


def normalize_name(name: str) -> str:
    return " ".join((name or "").strip().split())


def build_source_tag_set() -> Tuple[Set[str], List[Tuple[str, int, str]]]:
    """Returns (unique_names, detailed_rows)."""
    source_rows: List[Tuple[str, int, str]] = []
    unique_names: Set[str] = set()

    source_models = [
        "res.partner.category",  # contact tags
        "crm.tag",               # sales/opportunity tags used in this repo
        "sale.order.tag",        # optional, if present in this Odoo build
    ]

    for model in source_models:
        if not model_exists(model):
            continue
        rows = read_tags(model)
        for r in rows:
            tag_name = normalize_name(str(r.get("name", "")))
            if not tag_name:
                continue
            source_rows.append((model, int(r.get("id", 0)), tag_name))
            unique_names.add(tag_name)

    return unique_names, source_rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed project.tags from contact/sales tags.")
    parser.add_argument("--apply", action="store_true", help="Create missing project.tags records")
    args = parser.parse_args()

    dry_run = not args.apply
    mode = "DRY RUN" if dry_run else "APPLY"

    print("=" * 80)
    print(f"SEED PROJECT/TASK TAGS FROM CONTACT + SALES TAGS ({mode})")
    print("=" * 80)

    if not model_exists("project.tags"):
        print("[ERROR] project.tags model is not available in this Odoo database.")
        return 1

    source_unique_names, source_rows = build_source_tag_set()
    print(f"[*] Source rows scanned: {len(source_rows)}")
    print(f"[*] Unique source tag names: {len(source_unique_names)}")

    existing_project_tags = read_tags("project.tags")
    existing_by_name = {normalize_name(str(r.get("name", ""))): int(r.get("id")) for r in existing_project_tags if normalize_name(str(r.get("name", "")))}

    print(f"[*] Existing project.tags: {len(existing_by_name)}")

    missing_names = sorted([name for name in source_unique_names if name not in existing_by_name])
    print(f"[*] Missing in project.tags: {len(missing_names)}")

    created_rows: List[Tuple[str, str, int | str]] = []
    if dry_run:
        for name in missing_names:
            created_rows.append(("project.tags", name, "DRY_RUN_NO_CREATE"))
    else:
        for name in missing_names:
            new_id = create_project_tag(name)
            created_rows.append(("project.tags", name, new_id))
            print(f"[OK] Created project tag: {name} (id={new_id})")

    with open(REPORT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["mode", mode])
        writer.writerow([])
        writer.writerow(["section", "model", "source_id", "tag_name", "status", "project_tag_id"])

        for model, src_id, tag_name in source_rows:
            status = "already_in_project_tags" if tag_name in existing_by_name else "missing_from_project_tags"
            pid = existing_by_name.get(tag_name, "")
            writer.writerow(["source_scan", model, src_id, tag_name, status, pid])

        for _, tag_name, project_tag_id in created_rows:
            writer.writerow(["create_action", "project.tags", "", tag_name, "created" if not dry_run else "dry_run", project_tag_id])

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Mode:                  {mode}")
    print(f"Source unique tags:    {len(source_unique_names)}")
    print(f"Already in project:    {len(source_unique_names) - len(missing_names)}")
    print(f"Missing before run:    {len(missing_names)}")
    print(f"Created this run:      {0 if dry_run else len(missing_names)}")
    print(f"Report written:        {REPORT_PATH}")

    if dry_run:
        print("\n[OK] Dry-run complete. Re-run with --apply to create missing project.tags.")
    else:
        print("\n[OK] Apply complete.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"[FATAL] {exc}")
        raise
