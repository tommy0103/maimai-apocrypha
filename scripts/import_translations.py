import argparse
import csv
import json
import logging
import re
from pathlib import Path


DEFAULT_DATA_DIR = Path("../raw_data")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def normalize_header(text: str) -> str:
    # Normalize headers so English/Chinese variants can be matched:
    # - strip all whitespace
    # - lower-case
    return re.sub(r"\s+", "", text or "").lower()


def pick_column(headers, candidates):
    # Try to find a header by multiple possible names.
    # Example: "area_id" / "区域ID" / "id" all map to the same column.
    normalized = {normalize_header(h): h for h in headers}
    for candidate in candidates:
        key = normalize_header(candidate)
        if key in normalized:
            return normalized[key]
    return None


def parse_path(path: str):
    # Parse a path like "characters[0].summary" into tokens:
    # [("characters", 0), ("summary", None)]
    tokens = []
    parts = path.split(".")
    index_pattern = re.compile(r"^([^\[\]]+)(?:\[(\d+)])?$")
    for part in parts:
        match = index_pattern.match(part)
        if not match:
            raise ValueError(f"Invalid path segment: {part}")
        key = match.group(1)
        idx = match.group(2)
        if idx is None:
            tokens.append((key, None))
        else:
            tokens.append((key, int(idx)))
    return tokens


def ensure_list_size(items, size):
    # Grow list to ensure items[size] is a valid index.
    while len(items) <= size:
        items.append({})


def set_path_value(target: dict, path: str, value: str) -> None:
    # Walk the tokenized path and create dict/list nodes on demand,
    # then set the final value.
    tokens = parse_path(path)
    current = target
    for i, (key, idx) in enumerate(tokens):
        is_last = i == len(tokens) - 1
        if idx is None:
            if is_last:
                current[key] = value
                return
            if key not in current or not isinstance(current[key], (dict, list)):
                current[key] = {}
            current = current[key]
            continue

        if key not in current or not isinstance(current[key], list):
            current[key] = []
        items = current[key]
        ensure_list_size(items, idx)
        if is_last:
            items[idx] = value
            return
        if not isinstance(items[idx], dict):
            items[idx] = {}
        current = items[idx]


def path_exists(base: dict, path: str) -> bool:
    tokens = parse_path(path)
    current = base
    for i, (key, idx) in enumerate(tokens):
        is_last = i == len(tokens) - 1
        if idx is None:
            if not isinstance(current, dict) or key not in current:
                return False
            if is_last:
                return True
            current = current[key]
            continue

        if not isinstance(current, dict) or key not in current:
            return False
        items = current[key]
        if not isinstance(items, list) or idx >= len(items):
            return False
        if is_last:
            return True
        current = items[idx]
    return False


def get_path_value(base: dict, path: str):
    tokens = parse_path(path)
    current = base
    for i, (key, idx) in enumerate(tokens):
        is_last = i == len(tokens) - 1
        if idx is None:
            if not isinstance(current, dict) or key not in current:
                return None
            if is_last:
                return current[key]
            current = current[key]
            continue

        if not isinstance(current, dict) or key not in current:
            return None
        items = current[key]
        if not isinstance(items, list) or idx >= len(items):
            return None
        if is_last:
            return items[idx]
        current = items[idx]
    return None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Import translation CSV into *.zh.json")
    parser.add_argument("csv_file", help="Feishu CSV export file path")
    parser.add_argument("--lang", default="zh")
    parser.add_argument("--data-dir", default=str(DEFAULT_DATA_DIR))
    parser.add_argument("--area-id", action="append", default=[], help="Limit to specific area id")
    parser.add_argument(
        "--strict",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require path to exist in base JSON",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes to *.zh.json (default is review only)",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Review each change and approve interactively (implies --apply)",
    )
    parser.add_argument(
        "--report",
        default=None,
        help="Optional path to write a review report (markdown)",
    )
    parser.add_argument("--log-level", default="INFO")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(levelname)s: %(message)s")

    csv_path = Path(args.csv_file)
    data_dir = Path(args.data_dir)

    if args.interactive:
        args.apply = True

    # "utf-8-sig" handles BOM from some CSV exports.
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        area_col = pick_column(headers, ["area_id", "areaid", "id", "区域id", "区域ID"])
        path_col = pick_column(headers, ["path", "field", "字段", "字段路径"])
        text_col = pick_column(headers, ["text", "translation", "译文", "翻译", "翻译内容"])

        if not area_col or not path_col or not text_col:
            raise SystemExit(
                "CSV columns not found. Required: area_id, path, text "
                "(or use Chinese headers like 区域ID / 字段路径 / 译文)."
            )

        by_area: dict[str, list[tuple[str, str]]] = {}
        for row in reader:
            area_id = (row.get(area_col) or "").strip()
            path = (row.get(path_col) or "").strip()
            text = (row.get(text_col) or "").strip()
            if not area_id or not path or not text:
                continue
            if args.area_id and area_id not in args.area_id:
                continue
            by_area.setdefault(area_id, [])
            by_area[area_id].append((path, text))

    if not by_area:
        raise SystemExit("No valid entries found in CSV.")

    review_lines: list[str] = []
    for area_id, entries in by_area.items():
        base_path = data_dir / f"{area_id}.json"
        base_data = None
        if args.strict:
            if not base_path.exists():
                logging.warning("Base JSON not found, skipping: %s", base_path)
                continue
            base_data = load_json(base_path)

        zh_path = data_dir / f"{area_id}.{args.lang}.json"
        if zh_path.exists():
            data = load_json(zh_path)
        else:
            data = {"id": area_id}

        review_lines.append(f"## {area_id}")
        review_lines.append("")
        applied_count = 0
        skipped_count = 0
        for path, text in entries:
            if args.strict and base_data is not None and not path_exists(base_data, path):
                logging.warning("Path not found in base JSON, skipping: %s (%s)", area_id, path)
                skipped_count += 1
                continue
            current_value = get_path_value(data, path)
            if current_value == text:
                skipped_count += 1
                continue
            review_lines.append(f"- path: `{path}`")
            review_lines.append(f"  - before: {repr(current_value)}")
            review_lines.append(f"  - after: {repr(text)}")
            review_lines.append("")

            if args.interactive:
                print(f"\n[{area_id}] {path}")
                print(f"  before: {repr(current_value)}")
                print(f"  after : {repr(text)}")
                decision = input("Apply this change? [y/N/q] ").strip().lower()
                if decision == "q":
                    raise SystemExit("Stopped by user.")
                if decision != "y":
                    skipped_count += 1
                    continue

            set_path_value(data, path, text)
            applied_count += 1

        review_lines.append(f"- applied: {applied_count}")
        review_lines.append(f"- skipped: {skipped_count}")
        review_lines.append("")

        if args.apply:
            save_json(zh_path, data)
            logging.info("Updated: %s (%s entries)", zh_path, applied_count)
        else:
            logging.info("Review only: %s (%s entries)", zh_path, applied_count)

    if args.report:
        report_path = Path(args.report)
        report_path.write_text("\n".join(review_lines), encoding="utf-8")
        logging.info("Review report written: %s", report_path)
    else:
        print("\n".join(review_lines))


if __name__ == "__main__":
    main()
