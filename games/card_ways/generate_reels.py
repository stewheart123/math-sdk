"""Generate BR0, FR0, and MR0 reel strips from CARDZ weight tables."""

import os
import random

REELS_PATH = os.path.join(os.path.dirname(__file__), "reels")

BOARD_WEIGHTS = {
    "A": 0.111,
    "K": 0.111,
    "Q": 0.111,
    "J": 0.111,
    "10": 0.123,
    "9": 0.111,
    "W": 0.063,
    "S": 0.087,
    "N": 0.171,
}

MODIFIER_WEIGHTS = {"X1": 0.80, "X2": 0.15, "X3": 0.05}

STRIP_LENGTH = 1000


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


def write_five_reel_csv(path, columns):
    length = len(columns[0])
    with open(path, "w", encoding="UTF-8", newline="\n") as f:
        for row in range(length):
            f.write(",".join(columns[reel][row] for reel in range(5)) + "\n")


def filter_weights(weights, exclude):
    return {s: w for s, w in weights.items() if s not in exclude}


def main():
    random.seed(42)

    br0_reel1 = build_column(filter_weights(BOARD_WEIGHTS, {"W", "S"}))
    br0_full = build_column(BOARD_WEIGHTS)
    br0_columns = [br0_reel1] + [list(br0_full) for _ in range(4)]
    for col in br0_columns[1:]:
        random.shuffle(col)
    write_five_reel_csv(os.path.join(REELS_PATH, "BR0.csv"), br0_columns)

    fr0_reel1 = build_column(filter_weights(BOARD_WEIGHTS, {"W", "S"}))
    fr0_other = build_column(filter_weights(BOARD_WEIGHTS, {"S"}))
    fr0_columns = [fr0_reel1] + [list(fr0_other) for _ in range(4)]
    for col in fr0_columns[1:]:
        random.shuffle(col)
    write_five_reel_csv(os.path.join(REELS_PATH, "FR0.csv"), fr0_columns)

    mr0 = build_column(MODIFIER_WEIGHTS, total=100)
    with open(os.path.join(REELS_PATH, "MR0.csv"), "w", encoding="UTF-8", newline="\n") as f:
        for sym in mr0:
            f.write(sym + "\n")

    print("Generated BR0.csv, FR0.csv, MR0.csv")


if __name__ == "__main__":
    main()
