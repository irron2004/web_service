"""Audit helper for the workplace (coworker) perception module.

Paste the JSON array of 48 workplace items into RAW_JSON to run standalone,
 or supply a path to a JSON file via --path.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict

POLE_SIGN = {"E": 1, "S": 1, "T": 1, "J": 1, "I": -1, "N": -1, "F": -1, "P": -1}
DIM_POLES = {"EI": {"E", "I"}, "SN": {"S", "N"}, "TF": {"T", "F"}, "JP": {"J", "P"}}

RAW_JSON = """[]""".strip()


def load_items(path: str | None) -> list[dict]:
    if path:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    else:
        if not RAW_JSON:
            raise SystemExit("RAW_JSON is empty—either paste the list or provide --path")
        data = json.loads(RAW_JSON)
    if not isinstance(data, list):  # type: ignore[unreachable]
        raise TypeError("Input must be a JSON array of question dictionaries")
    return data


def audit(items: list[dict]) -> None:
    ids = [item.get("id") for item in items]
    dup_ids = [code for code, count in Counter(ids).items() if count > 1]
    if dup_ids:
        print("❌ Duplicate IDs detected:", dup_ids)
        sys.exit(1)

    dim_counts = Counter(item.get("dim") for item in items)
    pole_counts = Counter(item.get("keyed_pole") for item in items)
    reverse_count = sum(1 for item in items if item.get("reverse_keyed"))
    total = len(items)

    bad_dim = [item["id"] for item in items if item.get("keyed_pole") not in DIM_POLES.get(item.get("dim"), set())]
    bad_sign = [item["id"] for item in items if POLE_SIGN.get(item.get("keyed_pole")) != item.get("sign")]
    bad_reverse = [item["id"] for item in items if bool(item.get("reverse_keyed")) != (item.get("keyed_pole") in {"I", "N", "F", "P"})]

    per_dim_pole = defaultdict(Counter)
    for item in items:
        per_dim_pole[item["dim"]][item["keyed_pole"]] += 1

    print("=== Workplace Module Audit ===")
    print(f"items: {total} (target 48)")
    print(f"reverse_keyed: {reverse_count} ({reverse_count/total:.1%})")
    print("by_dim:", dict(dim_counts))
    print("by_pole:", dict(pole_counts))
    print("per_dim breakdown:")
    for dim, counts in per_dim_pole.items():
        print(f"  {dim}: {dict(counts)}")

    if bad_dim or bad_sign or bad_reverse:
        if bad_dim:
            print("❌ keyed_pole not in dimension:", bad_dim)
        if bad_sign:
            print("❌ sign mismatch keyed pole:", bad_sign)
        if bad_reverse:
            print("❌ reverse_keyed flag inconsistent:", bad_reverse)
    else:
        print("✅ all structural checks passed")

    if not (40 <= total <= 56):
        print("⚠️ item count out of recommended range (40–56)")
    if reverse_count / total < 0.4:
        print("⚠️ reverse-keyed ratio below 40%")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit workplace module questions")
    parser.add_argument("--path", help="Path to JSON array of items", default=None)
    args = parser.parse_args()

    items = load_items(args.path)
    audit(items)


if __name__ == "__main__":
    main()
