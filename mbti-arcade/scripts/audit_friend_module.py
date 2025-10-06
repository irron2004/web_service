"""Audit helper for the friend perception module."""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict

POLE_SIGN = {"E": 1, "S": 1, "T": 1, "J": 1, "I": -1, "N": -1, "F": -1, "P": -1}
DIM_POLES = {"EI": {"E", "I"}, "SN": {"S", "N"}, "TF": {"T", "F"}, "JP": {"J", "P"}}
RAW_JSON = """[]""".strip()


def load_items(path: str | None) -> list[dict]:
    if path:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    if not RAW_JSON:
        raise SystemExit("RAW_JSON is empty; provide --path or embed the dataset")
    return json.loads(RAW_JSON)


def audit(items: list[dict]) -> None:
    ids = [item.get("id") for item in items]
    duplicates = [code for code, count in Counter(ids).items() if count > 1]
    if duplicates:
        raise SystemExit(f"Duplicate IDs detected: {duplicates}")

    total = len(items)
    dim_counts = Counter(item.get("dim") for item in items)
    pole_counts = Counter(item.get("keyed_pole") for item in items)
    reverse_count = sum(1 for item in items if item.get("reverse_keyed"))

    per_dim = defaultdict(Counter)
    bad_dim, bad_sign, bad_rev = [], [], []
    for item in items:
        dim = item.get("dim")
        pole = item.get("keyed_pole")
        per_dim[dim][pole] += 1
        if pole not in DIM_POLES.get(dim, set()):
            bad_dim.append(item["id"])
        if POLE_SIGN.get(pole) != item.get("sign"):
            bad_sign.append(item["id"])
        expected_reverse = pole in {"I", "N", "F", "P"}
        if bool(item.get("reverse_keyed")) != expected_reverse:
            bad_rev.append(item["id"])

    print("=== FRIEND MODULE AUDIT ===")
    print(f"total: {total} (target 48)")
    print(f"reverse_keyed: {reverse_count} ({reverse_count/total:.1%})")
    print("by_dim:", dict(dim_counts))
    print("by_pole:", dict(pole_counts))
    print("per_dim breakdown:")
    for dim, counter in per_dim.items():
        print(f"  {dim}: {dict(counter)}")

    if bad_dim:
        print("❌ keyed_pole not within dimension:", bad_dim)
    if bad_sign:
        print("❌ sign does not match pole:", bad_sign)
    if bad_rev:
        print("❌ reverse_keyed flag inconsistent:", bad_rev)

    if not (40 <= total <= 56):
        print("⚠️ item count outside recommended 40–56 range")
    if total and reverse_count / total < 0.4:
        print("⚠️ reverse-keyed ratio below 40%")


def main() -> None:
    parser = argparse.ArgumentParser(description="Audit friend module question list")
    parser.add_argument("--path", help="Path to JSON file with friend items", default=None)
    args = parser.parse_args()

    audit(load_items(args.path))


if __name__ == "__main__":
    main()
