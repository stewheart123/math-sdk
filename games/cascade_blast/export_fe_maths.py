"""Copy FE config and sample books into export_maths/ for frontend integration.

Prefers library/publish_files/*.jsonl.zst (current 10k books) so LUTs stay intact.
Falls back to library/books JSON/JSONL.
"""
import io
import json
import os
import shutil

import zstandard as zstd

GAME_DIR = os.path.dirname(__file__)
LIBRARY = os.path.join(GAME_DIR, "library")
PUBLISH = os.path.join(LIBRARY, "publish_files")
EXPORT_DIR = os.path.join(GAME_DIR, "export_maths")
SAMPLE_COUNT = 100

MODES = [
    "base",
    "bonus_hotspots",
    "bonus_volatile",
    "bonus_fs",
]

CONFIG_SRC = os.path.join(LIBRARY, "configs", "config_fe_cascade_blast.json")
CONFIG_DST = os.path.join(EXPORT_DIR, "config_fe_cascade_blast.json")


def iter_books(path):
    if path.endswith(".zst"):
        with open(path, "rb") as f:
            with zstd.ZstdDecompressor().stream_reader(f) as reader:
                txt_stream = io.TextIOWrapper(reader, encoding="utf-8")
                for line in txt_stream:
                    line = line.strip()
                    if line:
                        yield json.loads(line)
        return
    if path.endswith(".json"):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"Expected JSON array in {path}")
        yield from data
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def resolve_book_path(mode):
    zst = os.path.join(PUBLISH, f"books_{mode}.jsonl.zst")
    if os.path.isfile(zst):
        return zst
    base = os.path.join(LIBRARY, "books", f"books_{mode}")
    for ext in (".jsonl", ".json"):
        path = base + ext
        if os.path.isfile(path):
            return path
    raise FileNotFoundError(f"Missing books for {mode} in publish_files/ or library/books/")


def event_types(book):
    return {e.get("type") for e in book.get("events", [])}


def event_of(book, event_type):
    for event in book.get("events", []):
        if event.get("type") == event_type:
            return event
    return None


def count_events(book, event_type):
    return sum(1 for e in book.get("events", []) if e.get("type") == event_type)


def pick_sample_books(books, count=SAMPLE_COUNT):
    """Spread 100 books across zero / win / FS / explosion / forcePair."""
    quotas = {
        "fs": 25,
        "force_pair": 20,
        "explosion": 25,
        "win": 20,
        "zero": 15,
    }
    buckets = {label: [] for label in quotas}
    leftovers = []

    for book in books:
        types = event_types(book)
        if "forcePair" in types:
            label = "force_pair"
        elif "freeSpinTrigger" in types:
            label = "fs"
        elif "explosion" in types:
            label = "explosion"
        elif book.get("payoutMultiplier", 0) > 0:
            label = "win"
        else:
            label = "zero"
        if len(buckets[label]) < quotas[label]:
            buckets[label].append(book)
        elif sum(len(v) for v in buckets.values()) + len(leftovers) < count:
            leftovers.append(book)

    picked = []
    seen = set()
    for label in quotas:
        for book in buckets[label]:
            book_id = book.get("id")
            if book_id in seen:
                continue
            seen.add(book_id)
            picked.append(book)
    for book in leftovers:
        if len(picked) >= count:
            break
        book_id = book.get("id")
        if book_id in seen:
            continue
        seen.add(book_id)
        picked.append(book)
    return picked[:count]


def pick_curated_samples(books, mode_name):
    """Pick a small diverse set for FE mock data / Storybook."""
    criteria = {
        "zero": lambda b: b.get("payoutMultiplier", 0) == 0,
        "win": lambda b: b.get("payoutMultiplier", 0) > 0,
        "pay_tumble": lambda b: "winInfo" in event_types(b),
        "explosion_normal": lambda b: any(
            e.get("type") == "explosion" and e.get("mode") == "normal" for e in b.get("events", [])
        ),
        "explosion_volatile": lambda b: any(
            e.get("type") == "explosion" and e.get("mode") == "volatile" for e in b.get("events", [])
        ),
        "freegame": lambda b: any(
            e.get("type") == "freeSpinTrigger" and e.get("totalFs") == 10 for e in b.get("events", [])
        ),
        "bonus_area_reveal": lambda b: "bonusAreaReveal" in event_types(b),
        "bonus_area_update": lambda b: "bonusAreaUpdate" in event_types(b),
        "force_pair": lambda b: "forcePair" in event_types(b),
        "three_plus_explosions": lambda b: count_events(b, "explosion") >= 3,
    }

    if mode_name == "bonus_hotspots":
        criteria["five_bonus_tiles"] = lambda b: (
            (event_of(b, "bonusAreaReveal") or {}).get("positions") or []
        ) and len((event_of(b, "bonusAreaReveal") or {}).get("positions") or []) >= 5
    elif mode_name == "bonus_fs":
        criteria["guaranteed_fs"] = lambda b: "freeSpinTrigger" in event_types(b)

    picks = {}
    for label, pred in criteria.items():
        for book in books:
            if pred(book) and label not in picks:
                picks[label] = book
                break
    return picks


def write_jsonl(path, books):
    with open(path, "w", encoding="utf-8") as f:
        for book in books:
            f.write(json.dumps(book, separators=(",", ":")) + "\n")


def main():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    samples_dir = os.path.join(EXPORT_DIR, "samples")
    events_dir = os.path.join(EXPORT_DIR, "events")
    os.makedirs(samples_dir, exist_ok=True)
    os.makedirs(events_dir, exist_ok=True)

    shutil.copy2(CONFIG_SRC, CONFIG_DST)

    configs_dir = os.path.join(LIBRARY, "configs")
    for mode in MODES:
        src = os.path.join(configs_dir, f"event_config_{mode}.json")
        if os.path.isfile(src):
            shutil.copy2(src, os.path.join(events_dir, f"event_config_{mode}.json"))

    manifest = {
        "gameID": "cascade_blast",
        "config": "config_fe_cascade_blast.json",
        "books": {},
        "curated_samples": {},
        "event_catalogs": {},
        "bet_modes": {
            "base": {"cost": 1.0, "buyBonus": False},
            "bonus_hotspots": {"cost": 2.1, "buyBonus": True},
            "bonus_volatile": {"cost": 6.6, "buyBonus": True},
            "bonus_fs": {"cost": 11.8, "buyBonus": True},
        },
    }

    for mode in MODES:
        src = resolve_book_path(mode)
        print(f"Loading {src} ...")
        books = list(iter_books(src))
        print(f"  {len(books)} books")
        sample = pick_sample_books(books, SAMPLE_COUNT)
        export_name = f"books_{mode}.jsonl"
        write_jsonl(os.path.join(EXPORT_DIR, export_name), sample)
        manifest["books"][mode] = export_name

        curated = pick_curated_samples(books, mode)
        sample_path = os.path.join(samples_dir, f"{mode}_samples.json")
        with open(sample_path, "w", encoding="utf-8") as f:
            json.dump(curated, f, indent=2)
        manifest["curated_samples"][mode] = {
            "file": f"samples/{mode}_samples.json",
            "scenarios": list(curated.keys()),
        }

        catalog = os.path.join(events_dir, f"event_config_{mode}.json")
        if os.path.isfile(catalog):
            manifest["event_catalogs"][mode] = f"events/event_config_{mode}.json"

        print(f"  {mode}: {len(sample)} books, {len(curated)} curated scenarios")
        del books

    manifest_path = os.path.join(EXPORT_DIR, "manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print(f"Exported to {EXPORT_DIR}")


if __name__ == "__main__":
    main()
