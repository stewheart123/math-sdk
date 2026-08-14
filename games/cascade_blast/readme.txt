# Cascade Blast

7x7 pay-anywhere cascade. 8+ matching symbols pay, disappear, then gravity fills the gaps. After paying cascades settle, adjacent SA (left) + SB (right) pairs explode and tumble. Repeat until there are no pays and no pairs.

## Symbols

* Paying: H1, H2, H3, H4, L1, L2, L3, L4 (hierarchy high to low)
* Special: S (free spins), SA, SB (explosives)
* Filler: N (does not pay). Needed so 8-of-a-kind is not almost automatic on a 7x7 with only 8 paying symbols.
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

* bonus_hotspots (2.3x): 5 unique bonus-area cells on the same 7x7 frame.
* bonus_volatile (15.7x): VR0 paying-dense reels, 3 bonus tiles, at least 3 volatile blasts per spin. Extra natural pairs also explode volatile.
* bonus_fs (17.8x): always enter 10 free spins after the base spin settles, even if S drifted off the highlight.

Buy costs snapped to EV / 0.965 from the natural probe.

bonus_volatile has no 0-win simulation fence: a guaranteed explosion almost always pays, so forcing 0x books does not terminate.

## v1 notes

Pass 2 nerfed 8-count pays and added filler N. Probe natural rates with:

    python games/cascade_blast/measure_natural.py

Optimizer is still disabled in run.py.
