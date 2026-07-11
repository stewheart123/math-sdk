"""Copy FE config and sample books into export_maths/ for frontend integration."""
import json
import os
import shutil

GAME_DIR = os.path.dirname(__file__)
LIBRARY = os.path.join(GAME_DIR, "library")
EXPORT_DIR = os.path.join(GAME_DIR, "export_maths")

BOOK_FILES = [
    "books_base.jsonl",
    "books_bonus_3.jsonl",
    "books_bonus_4.jsonl",
    "books_bonus_5.jsonl",
]

CONFIG_SRC = os.path.join(LIBRARY, "configs", "config_fe_card_ways.json")
CONFIG_DST = os.path.join(EXPORT_DIR, "config_fe_card_ways.json")


def load_books(path):
    books = []
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        raise ValueError(f"Expected JSON array in {path}")
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                books.append(json.loads(line))
    return books


def resolve_book_path(mode_file):
    base = os.path.join(LIBRARY, "books", os.path.splitext(mode_file)[0])
    for ext in (".jsonl", ".json"):
        path = base + ext
        if os.path.isfile(path):
            return path, mode_file if ext == ".jsonl" else mode_file.replace(".jsonl", ".json")
    raise FileNotFoundError(f"Missing books for {mode_file} in library/books/")


def pick_curated_samples(books, mode_name):
    """Pick a small diverse set for FE mock data."""
    picks = {}
    criteria = {
        "base_zero": lambda b: b.get("criteria") == "0",
        "base_win": lambda b: b.get("criteria") == "basegame" and b.get("payoutMultiplier", 0) > 0,
        "base_freegame_10": lambda b: any(
            e.get("type") == "freeSpinTrigger" and e.get("totalFs") == 10 for e in b.get("events", [])
        ),
        "base_freegame_15": lambda b: any(
            e.get("type") == "freeSpinTrigger" and e.get("totalFs") == 15 for e in b.get("events", [])
        ),
        "base_freegame_20": lambda b: any(
            e.get("type") == "freeSpinTrigger" and e.get("totalFs") == 20 for e in b.get("events", [])
        ),
        "modifier_x2": lambda b: any(
            e.get("type") == "modifierReveal" and e.get("multiplier") == 2 for e in b.get("events", [])
        ),
        "modifier_x3": lambda b: any(
            e.get("type") == "modifierReveal" and e.get("multiplier") == 3 for e in b.get("events", [])
        ),
        "any_win": lambda b: b.get("payoutMultiplier", 0) > 0,
    }

    if mode_name != "base":
        criteria = {
            f"{mode_name}_win": lambda b: b.get("payoutMultiplier", 0) > 0,
            f"{mode_name}_modifier_x2": lambda b: any(
                e.get("type") == "modifierReveal" and e.get("multiplier") == 2 for e in b.get("events", [])
            ),
            f"{mode_name}_modifier_x3": lambda b: any(
                e.get("type") == "modifierReveal" and e.get("multiplier") == 3 for e in b.get("events", [])
            ),
        }
        spins = {"bonus_3": 10, "bonus_4": 15, "bonus_5": 20}.get(mode_name)
        if spins:
            criteria[f"{mode_name}_spins"] = lambda b, s=spins: any(
                e.get("type") == "freeSpinTrigger" and e.get("totalFs") == s for e in b.get("events", [])
            )

    for label, pred in criteria.items():
        for book in books:
            if pred(book) and label not in picks:
                picks[label] = book
                break

    return picks


def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    samples_dir = os.path.join(EXPORT_DIR, "samples")
    os.makedirs(samples_dir, exist_ok=True)

    shutil.copy2(CONFIG_SRC, CONFIG_DST)

    mode_map = {
        "books_base.jsonl": "base",
        "books_bonus_3.jsonl": "bonus_3",
        "books_bonus_4.jsonl": "bonus_4",
        "books_bonus_5.jsonl": "bonus_5",
    }

    manifest = {"config": "config_fe_card_ways.json", "books": {}, "curated_samples": {}}

    for book_file in BOOK_FILES:
        src, export_name = resolve_book_path(book_file)
        if not os.path.isfile(src):
            raise FileNotFoundError(f"Missing {src}. Run run_fe_samples.py first.")

        dst = os.path.join(EXPORT_DIR, export_name)
        shutil.copy2(src, dst)
        mode = mode_map[book_file]
        manifest["books"][mode] = export_name

        books = load_books(src)
        curated = pick_curated_samples(books, mode)
        sample_path = os.path.join(samples_dir, f"{mode}_samples.json")
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(curated, f, indent=2)
        manifest["curated_samples"][mode] = {
            "file": f"samples/{mode}_samples.json",
            "scenarios": list(curated.keys()),
        }

    manifest_path = os.path.join(EXPORT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Exported to {EXPORT_DIR}")
    for mode, info in manifest["curated_samples"].items():
        print(f"  {mode}: {len(info['scenarios'])} curated scenarios -> {info['file']}")


if __name__ == "__main__":
    main()
