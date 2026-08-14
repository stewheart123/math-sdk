"""Generate BR0, FR0, and WCAP reel strips from weight tables."""

import os
import random

REELS_PATH = os.path.join(os.path.dirname(__file__), "reels")
NUM_REELS = 7
STRIP_LENGTH = 1000

# Weights sum to 100 so a 1000-stop strip is 10 copies per weight point.
BASE_WEIGHTS = {
    "H1": 4,
    "H2": 6,
    "H3": 8,
    "H4": 10,
    "L1": 12,
    "L2": 14,
    "L3": 16,
    "L4": 18,
    "SA": 6,
    "SB": 6,
}

FS_WEIGHTS = {
    "H1": 4,
    "H2": 6,
    "H3": 8,
    "H4": 10,
    "L1": 11,
    "L2": 13,
    "L3": 15,
    "L4": 17,
    "SA": 8,
    "SB": 8,
}

WCAP_WEIGHTS = {
    "H1": 20,
    "H2": 18,
    "H3": 14,
    "H4": 12,
    "L1": 6,
    "L2": 4,
    "L3": 4,
    "L4": 2,
    "SA": 10,
    "SB": 10,
}


def weights_to_counts(weights, total):
    symbols = list(weights.keys())
    raw = [weights[s] / sum(weights.values()) * total for s in symbols]
    counts = {s: int(v) for s, v in zip(symbols, raw)}
    remainder = total - sum(counts.values())
    if remainder:
        largest = max(symbols, key=lambda s: raw[symbols.index(s)] - counts[s])
        counts[largest] += remainder
    return counts


def build_column(weights, total=STRIP_LENGTH):
    counts = weights_to_counts(weights, total)
    column = []
    for sym, count in counts.items():
        column.extend([sym] * count)
    random.shuffle(column)
    return column


def write_reel_csv(path, columns):
    length = len(columns[0])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="UTF-8", newline="\n") as handle:
        for row in range(length):
            handle.write(",".join(columns[reel][row] for reel in range(len(columns))) + "\n")


def build_strips(weights):
    columns = [build_column(weights) for _ in range(NUM_REELS)]
    return columns


def main():
    random.seed(42)
    write_reel_csv(os.path.join(REELS_PATH, "BR0.csv"), build_strips(BASE_WEIGHTS))
    write_reel_csv(os.path.join(REELS_PATH, "FR0.csv"), build_strips(FS_WEIGHTS))
    write_reel_csv(os.path.join(REELS_PATH, "WCAP.csv"), build_strips(WCAP_WEIGHTS))
    print("Generated BR0.csv, FR0.csv, WCAP.csv")


if __name__ == "__main__":
    main()
