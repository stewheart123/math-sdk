# Cascade Blast

7x7 pay-anywhere cascade. 8+ matching symbols pay, disappear, then gravity fills the gaps. After paying cascades settle, adjacent SA (left) + SB (right) pairs explode and tumble. Repeat until there are no pays and no pairs.

## Symbols

* Paying: H1, H2, H3, H4, L1, L2, L3, L4 (hierarchy high to low)
* Special: S (free spins), SA, SB (explosives)
* No wilds in v1

Pays start at 8-of-a-kind anywhere. Bands: (8), (9-10), (11-13), (14-49).

## Bonus area

The bonus area is an existing cell on the 7x7 frame, highlighted as a backdrop. Any symbol can sit on it. It is chosen at the start of each base spin and does not move with gravity.

Base game always plants exactly one S on the initial drop (S is not on the reel strips, so tumbles cannot add more). S falls with gravity but cannot be destroyed by pays or explosions.

After the board fully settles, if S occupies a bonus-area cell, award 10 free spins. No retrigger. Free spins have no S and no bonus areas.

## Explosions

Checked only after paying wins have fully resolved.

* Pair = SA immediately left of SB on the same row.
* All current pairs explode simultaneously.
* Normal (base): destroy the pair plus every cell above them in those two columns (row 0 is the top).
* Volatile (free spins, and every explosion during bonus_volatile): full column through SA, full column through SB, and the entire shared row (~19 cells for one pair).
* Unpaired SA/SB elsewhere survive unless they sit inside another pair's blast.
* Gravity can split a pair during the pay phase; that pair then does not explode.

## Bonus buys

* bonus_hotspots (5x): 5 unique bonus-area cells on the same 7x7 frame.
* bonus_volatile (10x): at least one SA+SB pair after the first pay settle (force-placed if needed). All explosions this spin are volatile, including extra pairs that form later.
* bonus_fs (25x): always enter 10 free spins after the base spin settles, even if S drifted off the highlight.

Costs are placeholders until hit-rates are measured.

bonus_volatile has no 0-win simulation fence: a guaranteed explosion almost always pays, so forcing 0x books does not terminate.

## v1 notes

Reel weights and pay values are a first pass. Run books, inspect library/books, then retune. Optimizer is disabled in run.py.
