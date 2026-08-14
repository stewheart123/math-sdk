Cascade Blast — Frontend math export
====================================

Copy this entire folder into the FE project's "export maths" directory.

Contents
--------
config_fe_cascade_blast.json   Game config (7x7, 96.5% RTP, buy modes)
books_base.jsonl               100 sample base rounds
books_bonus_hotspots.jsonl     100 sample hotspot buys (5 tiles, cost 2.3x)
books_bonus_volatile.jsonl     100 sample volatile buys (3 tiles, cost 15.7x)
books_bonus_fs.jsonl           100 sample FS buys (always 10 FS, cost 17.8x)
samples/                       Curated scenario picks for Storybook mocks
events/                        One example payload per bookEvent type, per mode
manifest.json                  Index of files, modes, and scenario labels
README.txt                     This file (includes the web-sdk prompt below)

Bet modes (RGS mode names — must match upload)
----------------------------------------------
base              cost 1.0x    feature spin
bonus_hotspots    cost 2.3x    buyBonus
bonus_volatile    cost 15.7x   buyBonus
bonus_fs          cost 17.8x   buyBonus

RTP 96.5%. Max win 5000x. payoutMultiplier in books is integer cents (100 = 1.0x).

What this is NOT
----------------
Do not upload these 100-book jsonl files to Stake Engine. RGS uses the compressed
10k books + LUTs in library/publish_files/. This folder is for FE Storybook and
bookEvent handlers only.

Regenerate
----------
From games/cascade_blast (does not re-sim; slices existing library/books):

  python export_fe_maths.py

Only run run_fe_samples.py if you intentionally want a fresh 100-spin library.
That overwrites library/books and rebuilds LUTs from 100 sims.

================================================================
PASTE THIS PROMPT INTO THE WEB-SDK / FRONTEND-SDK CURSOR CHAT
================================================================

You are adapting a Stake Engine web-sdk game app to play Cascade Blast.

Math (uploaded to RGS) returns a book. The frontend does not compute wins.
It plays `book.events` in order. Copy the `export_maths` folder from math-sdk
`games/cascade_blast/export_maths/` into this app's export-maths / stories data
area. Use those JSONL books and `samples/*_samples.json` for Storybook
(`base_books.ts`, `bonus_books.ts`, `*_events.ts`).

Closest template: a pay-anywhere / cluster / tumble scatter game, NOT lines
and NOT card-ways. Fork the nearest tumble+scatter app.

------------------------------------------------
1. Identity (must match RGS upload)
------------------------------------------------
- gameID: cascade_blast
- workingName: Cascade Blast
- RTP: 96.5%
- max win: 5000x
- Grid: 7 reels x 7 rows
- Win type: scatter / pay-anywhere (8+ of a kind anywhere on the 7x7)
- No wilds

Bet modes:
- base            cost 1.0    feature=true   buyBonus=false
- bonus_hotspots  cost 2.3    feature=false  buyBonus=true
- bonus_volatile  cost 15.7   feature=false  buyBonus=true
- bonus_fs        cost 17.8   feature=false  buyBonus=true

Buy-bonus RGS calls use those exact mode names.

------------------------------------------------
2. Coordinates and padding
------------------------------------------------
include_padding is ON. Every reveal board is 7 columns x 9 rows:
  [0] = top padding symbol (not in the 7x7 window)
  [1]..[7] = visible 7x7 (math row 0 is the TOP of the window)
  [8] = bottom padding symbol

ALL position fields in events already use client/padded rows (math row + 1):
bonusAreaReveal, bonusAreaUpdate, explosion, forcePair, winInfo, tumbleBoard
explodingSymbols, freeSpinTrigger.

Visible cell (reel, mathRow) => event position { reel, row: mathRow + 1 }.

------------------------------------------------
3. Symbols
------------------------------------------------
Paying: H1, H2, H3, H4, L1, L2, L3, L4
Filler: N   (flag non_winnable: true — never pays, can be exploded/tumbled)
Special:
  S   scatter: true     free-spin symbol
  SA  bomb_a: true      left bomb
  SB  bomb_b: true      right bomb

Pay bands (count of matching paying symbol anywhere): 8 / 9-10 / 11-13 / 14+.
See config_fe_cascade_blast.json paytables. N, S, SA, SB never form a pay.

------------------------------------------------
4. How a spin works (play events, do not re-simulate)
------------------------------------------------
Base spin:
1. bonusAreaReveal — highlight existing 7x7 cell(s) as a BACKDROP on the frame.
   Not a separate overlay grid. Any symbol can sit on a highlighted cell.
   The highlight is chosen at spin start and does NOT move with gravity.
   Counts: base=1, bonus_hotspots=5, bonus_volatile=3, bonus_fs=1.
2. reveal — initial drop. Base always has exactly one S. S is not on reel
   strips; tumbles cannot add more S. S falls with gravity. S cannot be
   destroyed by pays or explosions.
3. Pay-tumble loop until no 8+ of a kind:
     winInfo -> updateTumbleWin -> tumbleBoard
4. Then SA+SB explosions (only after pays have fully settled):
     optional forcePair (volatile buy only, to guarantee min 3 blasts)
     explosion -> tumbleBoard
   Then back to step 3 if new 8+ pays appear. Repeat until no pays and no pairs.
5. setWin (if this spin paid) then setTotalWin.
6. After the board is fully settled: if S sits on a bonus-area cell, emit
   freeSpinTrigger (totalFs=10). bonus_fs buy always triggers 10 FS even if S
   drifted off the tile. No retrigger. FS has no S and no bonus areas.
   Forced-FS books may emit bonusAreaUpdate to snap a highlight under S
   before the trigger — animate the highlight moving, then trigger.
7. Free spins: updateFreeSpin, reveal (no bonusAreaReveal), same pay/explode
   loop with explosion.mode="volatile", setWin/setTotalWin. After 10 spins:
   freeSpinEnd, then finalWin.

Explosions:
- Pair = SA immediately LEFT of SB on the SAME row.
- All current pairs explode simultaneously.
- explosion.mode "normal" (base + bonus_hotspots base spin): destroy the pair
  plus every cell ABOVE them in those two columns (row 0 / client row 1 is top).
- explosion.mode "volatile" (all free spins, and every blast during
  bonus_volatile including the base spin): full column of SA + full column of
  SB + the entire shared row (~19 cells for one pair).
- explosion.pairs gives each SA/SB pair. explosion.positions is the union of
  cells to remove (already padded, S never included).
- Unpaired SA/SB survive unless they sit inside another pair's blast.
- Gravity during the pay phase can split a pair; that pair then does not explode.
- forcePair overwrites two adjacent non-S cells with SA+SB. Animate the
  transform, then the following explosion.

------------------------------------------------
5. bookEvent types to implement
------------------------------------------------
Standard:
  reveal, winInfo, updateTumbleWin, tumbleBoard, setWin, setTotalWin,
  finalWin, freeSpinTrigger, updateFreeSpin, freeSpinEnd

Custom (must add types + bookEventHandlerMap + Storybook):
  bonusAreaReveal   { type, positions: [{reel, row}] }
  bonusAreaUpdate   { type, positions: [{reel, row}] }
  forcePair         { type, positions: [{reel, row, symbol}, {reel, row, symbol}] }
                    always SA then SB, adjacent same row
  explosion         { type, mode: "normal"|"volatile", pairs: [{sa, sb}], positions }

There is no freeSpinRetrigger. There is no modifierReveal. There is no wild.

Example payloads: events/event_config_*.json
Full rounds: samples/<mode>_samples.json and books_<mode>.jsonl

Typical curated labels:
  zero, win, pay_tumble, explosion_normal, explosion_volatile, freegame,
  bonus_area_reveal, bonus_area_update, force_pair, three_plus_explosions,
  five_bonus_tiles (hotspots), three_bonus_tiles (volatile), guaranteed_fs (bonus_fs)

------------------------------------------------
6. Implementation checklist
------------------------------------------------
1. Fork closest tumble/scatter app. Set gameID to cascade_blast.
2. 7x7 window with padding row above and below. Wire symbols + flags.
3. Bonus-area backdrop on existing cells from bonusAreaReveal / Update.
   Do not invent a second board.
4. Play tumbleBoard (explodingSymbols + newSymbols falling from the top).
5. Handle explosion (normal vs volatile VFX) then tumbleBoard.
6. Handle forcePair before the guaranteed volatile blasts.
7. FS: 10 spins, no retrigger, no S, no bonus tiles, always volatile blasts.
8. Buy bonus UI: three products mapped to bonus_hotspots / bonus_volatile /
   bonus_fs at 2.3x / 15.7x / 17.8x.
9. Storybook: MODE_BASE + one story set per buy mode. Paste curated samples
   into bookEvent stories. Play books/random from the jsonl files.
10. Amounts: event amounts and payoutMultiplier are integer cents
    (100 = 1x bet).

Do not recompute pays, explosions, or FS from the board. Trust the events.
