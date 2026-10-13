"""Manual stromal TIL area-fraction calculator.

The caller supplies areas annotated by a qualified reviewer. This module does
not identify cell types, segment tissue, or make treatment recommendations.
"""

import argparse
import csv
import json
import math
from pathlib import Path


def _area(value, name):
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a finite number") from exc
    if not math.isfinite(result):
        raise ValueError(f"{name} must be a finite number")
    return result


def calculate_metrics(*, stromal_area, til_area):
    """Calculate 100 × occupied stromal area / total eligible stromal area.

    Values must use the same area unit. Stromal area must be positive and the
    TIL-occupied area must lie between zero and that area (inclusive).
    """
    stromal = _area(stromal_area, "stromal_area")
    occupied = _area(til_area, "til_area")
    if stromal <= 0:
        raise ValueError("stromal_area must be greater than zero")
    if occupied < 0:
        raise ValueError("til_area cannot be negative")
    if occupied > stromal:
        raise ValueError("til_area cannot exceed stromal_area")
    percentage = round(100.0 * (occupied / stromal), 2)
    return {
        "tool": "til-tumor-infiltrating-lymphocyte-scorer",
        "score": percentage,
        "stromal_til_percent": percentage,
        "classification": "Not assigned",
        "clinical_recommendation": "No treatment recommendation or universal cutoff is inferred.",
        "inputs_evaluated": 2,
    }


def process_batch(input_csv, output_csv):
    """Read CSV with stromal_area and til_area columns; fail on invalid rows."""
    source = Path(input_csv)
    if not source.is_file():
        raise FileNotFoundError(f"Input CSV not found: {source}")
    with source.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = list(reader.fieldnames or [])
        if not fields:
            raise ValueError("Input CSV is empty or has no headers")
        if len(fields) != len(set(fields)):
            raise ValueError("CSV contains duplicate headers")
        required = {"stromal_area", "til_area"}
        if not required.issubset(fields):
            raise ValueError("CSV must contain stromal_area and til_area columns")
        if "stromal_til_percent" in fields:
            raise ValueError("Input CSV already contains stromal_til_percent")
        out_rows = []
        for row_number, row in enumerate(reader, start=2):
            if None in row:
                raise ValueError(f"CSV row {row_number} has extra fields")
            try:
                result = calculate_metrics(
                    stromal_area=row["stromal_area"], til_area=row["til_area"]
                )
            except ValueError as exc:
                raise ValueError(f"CSV row {row_number}: {exc}") from exc
            out_rows.append({**row, "stromal_til_percent": result["score"]})
    dest = Path(output_csv)
    if source.resolve() == dest.resolve():
        raise ValueError("Input and output CSV paths must differ")
    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[*fields, "stromal_til_percent"])
        writer.writeheader()
        writer.writerows(out_rows)
    print(f"Processed {len(out_rows)} records -> {dest}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="Manual stromal TIL area-percentage calculator")
    subparsers = parser.add_subparsers(dest="command", required=True)
    single = subparsers.add_parser("single", help="Score one annotated stromal area")
    single.add_argument("--stromal-area", required=True, type=float)
    single.add_argument("--til-area", required=True, type=float)
    batch = subparsers.add_parser("batch", help="Score a CSV of annotated areas")
    batch.add_argument("-i", "--input", required=True)
    batch.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args(argv)
    if args.command == "single":
        print(json.dumps(calculate_metrics(
            stromal_area=args.stromal_area, til_area=args.til_area
        ), indent=2, allow_nan=False))
    else:
        process_batch(args.input, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
