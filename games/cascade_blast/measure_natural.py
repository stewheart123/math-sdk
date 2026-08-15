"""Natural-rate diagnostic: no book fences, no FS rejection, no LUT mix."""

import argparse
import statistics
import sys
from collections import Counter
from pathlib import Path

GAME_DIR = Path(__file__).resolve().parent
REPO_ROOT = GAME_DIR.parent.parent
sys.path.insert(0, str(GAME_DIR))
sys.path.insert(0, str(REPO_ROOT))

from game_config import GameConfig
from gamestate import GameState


def run_natural_spin(gs: GameState, sim: int) -> dict:
    """One spin including natural FS, without quota retries."""
    gs.reset_seed(sim)
    gs.reset_book()
    gs.repeat = False
    gs.draw_and_resolve_base()
    gs.win_manager.update_gametype_wins(gs.gametype)

    event_types = Counter(event["type"] for event in gs.book.events)
    base_win = round(gs.win_manager.running_bet_win, 4)
    scatter_on_bonus = gs.scatter_on_bonus_area()
    triggered = gs.check_fs_condition()
    if triggered:
        gs.run_freespin_from_base()

    gs.evaluate_finalwin()
    return {
        "payout": gs.final_win,
        "base_win": base_win,
        "fs_win": round(gs.win_manager.freegame_wins, 4),
        "triggered": triggered,
        "scatter_on_bonus": scatter_on_bonus,
        "explosions": event_types.get("explosion", 0),
        "pay_tumbles": event_types.get("winInfo", 0),
        "force_pair": event_types.get("forcePair", 0),
        "bonus_areas": len(gs.bonus_areas),
    }


def percentile(values, p):
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, int(round((p / 100) * (len(ordered) - 1)))))
    return ordered[idx]


def summarize(name: str, cost: float, rows: list[dict]) -> dict:
    n = len(rows)
    payouts = [row["payout"] for row in rows]
    base_wins = [row["base_win"] for row in rows]
    zeros = sum(1 for payout in payouts if payout <= 0)
    hits = n - zeros
    fs_rows = [row for row in rows if row["triggered"]]
    explosion_spins = sum(1 for row in rows if row["explosions"] > 0)
    avg_payout = statistics.fmean(payouts)
    avg_base = statistics.fmean(base_wins)
    avg_fs_contrib = statistics.fmean(row["fs_win"] for row in rows)
    fs_rate = len(fs_rows) / n if n else 0
    avg_fs_package = statistics.fmean(row["fs_win"] for row in fs_rows) if fs_rows else 0.0
    suggested_cost = round(avg_payout / 0.965, 2) if avg_payout else 0.0

    print(f"\n=== {name}  n={n}  cost={cost}x ===")
    print(f"hit_rate          {hits / n:.1%}   zeros {zeros / n:.1%}")
    print(f"avg_payout        {avg_payout:.3f}x   (p50 {percentile(payouts, 50):.2f}  p90 {percentile(payouts, 90):.2f}  max {max(payouts):.1f})")
    print(f"avg_base          {avg_base:.3f}x")
    print(f"avg_fs_contrib    {avg_fs_contrib:.3f}x")
    print(f"fs_rate           {fs_rate:.2%}   (1 in {1 / fs_rate:.1f})" if fs_rate else "fs_rate           0%")
    print(f"avg_fs_package    {avg_fs_package:.2f}x  (given trigger)")
    print(f"explosion_rate    {explosion_spins / n:.1%}   avg explosions/spin {statistics.fmean(row['explosions'] for row in rows):.2f}")
    print(f"avg pay-tumbles   {statistics.fmean(row['pay_tumbles'] for row in rows):.2f}")
    print(f"rtp vs cost       {avg_payout / cost:.1%}")
    print(f"suggested cost    {suggested_cost}x  (avg_payout / 0.965)")
    return {
        "mode": name,
        "n": n,
        "avg_payout": avg_payout,
        "suggested_cost": suggested_cost,
        "fs_rate": fs_rate,
    }


def main():
    parser = argparse.ArgumentParser(description="Natural Cascade Blast hit-rate probe")
    parser.add_argument("--spins", type=int, default=8000)
    parser.add_argument(
        "--modes",
        nargs="+",
        default=["base", "bonus_hotspots", "bonus_volatile", "bonus_fs"],
    )
    args = parser.parse_args()

    config = GameConfig()
    gs = GameState(config)
    costs = {mode.get_name(): mode.get_cost() for mode in config.bet_modes}

    for mode in args.modes:
        gs.betmode = mode
        gs.criteria = "basegame" if mode != "bonus_fs" else "freegame"
        rows = [run_natural_spin(gs, sim) for sim in range(1, args.spins + 1)]
        summarize(mode, costs[mode], rows)


if __name__ == "__main__":
    main()
