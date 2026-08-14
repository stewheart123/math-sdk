"""Generate BR0, FR0, and WCAP reel strips from weight tables."""

import os
import random

REELS_PATH = os.path.join(os.path.dirname(__file__), "reels")
NUM_REELS = 7
STRIP_LENGTH = 1000

# Weights sum to 100 so a 1000-stop strip is 10 copies per weight point.
# N is a non-paying filler so 8-of-a-kind is not almost automatic on a 7x7.
BASE_WEIGHTS = {
    "H1": 4,
    "H2": 5,
    "H3": 6,
    "H4": 7,
    "L1": 9,
    "L2": 10,
    "L3": 11,
    "L4": 12,
    "SA": 5,
    "SB": 5,
    "N": 26,
}

FS_WEIGHTS = {
    "H1": 5,
    "H2": 6,
    "H3": 7,
    "H4": 8,
    "L1": 9,
    "L2": 10,
    "L3": 11,
    "L4": 12,
    "SA": 12,
    "SB": 12,
    "N": 8,
}

WCAP_WEIGHTS = {
    "H1": 22,
    "H2": 18,
    "H3": 14,
    "H4": 12,
    "L1": 4,
    "L2": 3,
    "L3": 2,
    "L4": 2,
    "SA": 9,
    "SB": 9,
    "N": 5,
}

# Paying-dense strip for the volatile buy. Pairs are forced; value comes from post-blast cascades.
VOLATILE_WEIGHTS = {
    "H1": 6,
    "H2": 8,
    "H3": 9,
    "H4": 10,
    "L1": 11,
    "L2": 12,
    "L3": 13,
    "L4": 14,
    "SA": 6,
    "SB": 6,
    "N": 5,
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
    write_reel_csv(os.path.join(REELS_PATH, "VR0.csv"), build_strips(VOLATILE_WEIGHTS))
    write_reel_csv(os.path.join(REELS_PATH, "WCAP.csv"), build_strips(WCAP_WEIGHTS))
    print("Generated BR0.csv, FR0.csv, VR0.csv, WCAP.csv")


if __name__ == "__main__":
    main()
