CARDZ / card_ways — Frontend math export (Path B)
================================================

Copy this entire folder into your FE project's "export maths" directory.

Contents
--------
config_fe_card_ways.json   Game config (96.5% RTP, bonus_3/4/5 buy tiers)
books_base.jsonl           100 sample base rounds
books_bonus_3.jsonl        100 sample buys (3 scatters / 10 FS, cost 70x)
books_bonus_4.jsonl        100 sample buys (4 scatters / 15 FS, cost 100x)
books_bonus_5.jsonl        100 sample buys (5 scatters / 20 FS, cost 130x)
samples/                   Curated scenario picks for quick mock testing
manifest.json              Index of files and scenario labels

Bet modes (RGS mode names)
--------------------------
base      cost 1x
bonus_3   cost 70x   buyBonus
bonus_4   cost 100x  buyBonus
bonus_5   cost 130x  buyBonus

Regenerate
----------
From games/card_ways:
  python run_fe_samples.py
  python export_fe_maths.py

Remove old FE files if present: books_bonus.jsonl, single "bonus" mode config.
