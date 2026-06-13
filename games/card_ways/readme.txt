# CARDZ (card_ways)

5-reel, 2-row ways game with a separate single-slot modifier area.

## Main board symbols

* Paying: A, K, Q, J, 10, 9 (paytable from CARDZ tool JSON)
* W — Wild (substitutes for paying symbols; not on reel 1)
* S — Scatter (base game only; 3+ anywhere awards 10 free spins)
* N — Non-winnable filler (on reels; not in paytable; no ways payout)

Reel strip frequencies match CARDZ tool weights (sum to 1 per board). Regenerate
with `python generate_reels.py` after weight changes.

## Modifier area

Separate from the main grid; holds exactly one symbol per reveal.

* X1 — multiply current win by 1 (80%)
* X2 — multiply current win by 2 (15%)
* X3 — multiply current win by 3 (5%)

### Base game

A fresh modifier is drawn every spin and multiplies that spin's total ways win.

### Free spins

* 3+ scatters in base game → 10 free spins (4 or 5 scatters also award 10)
* Scatter symbols do not appear on free-spin reels (no retriggers)
* Modifier is drawn once when entering the feature and applies to all 10 spins
