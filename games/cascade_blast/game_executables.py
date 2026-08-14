"""Cascade Blast grouped spin actions: pays, bonus areas, and SA+SB explosions."""

import random

from game_calculations import GameCalculations
from game_events import (
    bonus_area_reveal_event,
    bonus_area_update_event,
    explosion_event,
    force_pair_event,
)
from src.calculations.scatter import Scatter
from src.events.events import fs_trigger_event, reveal_event, set_total_event, set_win_event


class GameExecutables(GameCalculations):
    """Game specific executable functions."""

    def draw_board(self, emit_event: bool = True, trigger_symbol: str = "scatter") -> None:
        """Draw a board without the stock scatter-count reject/force loop."""
        self.create_board_reelstrips()
        if self.gametype == self.config.basegame_type:
            self.implant_scatter()
            self.pick_bonus_areas()
            if emit_event:
                bonus_area_reveal_event(self)
        else:
            self.bonus_areas = []
            self.bonus_area_set = set()
        if emit_event:
            reveal_event(self)

    def implant_scatter(self) -> None:
        """Place exactly one FS symbol on the initial base drop."""
        reel = random.randrange(self.config.num_reels)
        row = random.randrange(self.config.num_rows[reel])
        self.board[reel][row] = self.create_symbol("S")
        self.get_special_symbols_on_board()

    def pick_bonus_areas(self) -> None:
        """Mark N unique cells on the existing 7x7 frame as bonus-area backdrops."""
        count = self.config.mode_bonus_areas.get(self.betmode, 1)
        cells = [
            (reel, row)
            for reel in range(self.config.num_reels)
            for row in range(self.config.num_rows[reel])
        ]
        chosen = random.sample(cells, count)
        self.bonus_areas = [{"reel": reel, "row": row} for reel, row in chosen]
        self.bonus_area_set = set(chosen)

    def scatter_on_bonus_area(self) -> bool:
        """True if the FS symbol currently sits on a highlighted frame cell."""
        for pos in self.special_syms_on_board.get("scatter", []):
            if (pos["reel"], pos["row"]) in self.bonus_area_set:
                return True
        return False

    def ensure_scatter_on_bonus_area(self) -> None:
        """Snap a bonus area under S so forced FS books do not need many retries."""
        scatter_positions = self.special_syms_on_board.get("scatter", [])
        if not scatter_positions:
            return
        pos = scatter_positions[0]
        target = (pos["reel"], pos["row"])
        if target in self.bonus_area_set:
            return
        if self.bonus_areas:
            old = self.bonus_areas[0]
            self.bonus_area_set.discard((old["reel"], old["row"]))
            self.bonus_areas[0] = {"reel": pos["reel"], "row": pos["row"]}
        else:
            self.bonus_areas = [{"reel": pos["reel"], "row": pos["row"]}]
        self.bonus_area_set.add(target)
        bonus_area_update_event(self)

    def protect_scatter_from_explode(self) -> None:
        """FS symbol cannot be destroyed by pays or explosions."""
        for pos in self.special_syms_on_board.get("scatter", []):
            self.board[pos["reel"]][pos["row"]].explode = False

    def get_scatterpays_update_wins(self) -> None:
        """Evaluate 8+ pay-anywhere wins and mark those symbols to tumble."""
        self.win_data = Scatter.get_scatterpay_wins(
            self.config, self.board, global_multiplier=self.global_multiplier
        )
        self.protect_scatter_from_explode()
        Scatter.record_scatter_wins(self)
        self.win_manager.tumble_win = self.win_data["totalWin"]
        self.win_manager.update_spinwin(self.win_data["totalWin"])

    def find_sa_sb_pairs(self) -> list:
        """Return (sa_reel, row) for every adjacent SA-left / SB-right pair."""
        pairs = []
        for reel in range(self.config.num_reels - 1):
            rows = self.config.num_rows[reel]
            for row in range(rows):
                if (
                    self.board[reel][row].name == "SA"
                    and self.board[reel + 1][row].name == "SB"
                ):
                    pairs.append((reel, row))
        return pairs

    def explosions_are_volatile(self) -> bool:
        """FS and the volatile buy use full-axis blasts; base uses 'above only'."""
        if self.gametype == self.config.freegame_type:
            return True
        return bool(self.config.mode_volatile_base.get(self.betmode, False))

    def blast_cells_for_pair(self, sa_reel: int, row: int, volatile: bool) -> set:
        """Cells destroyed by one SA+SB pair. Row 0 is the top of the frame."""
        cells = {(sa_reel, row), (sa_reel + 1, row)}
        sb_reel = sa_reel + 1
        num_rows = self.config.num_rows[sa_reel]
        if volatile:
            for blast_row in range(num_rows):
                cells.add((sa_reel, blast_row))
                cells.add((sb_reel, blast_row))
            for blast_reel in range(self.config.num_reels):
                cells.add((blast_reel, row))
        else:
            for blast_row in range(row):
                cells.add((sa_reel, blast_row))
                cells.add((sb_reel, blast_row))
        return cells

    def force_volatile_pair(self) -> bool:
        """Overwrite two adjacent non-S cells with SA+SB. Returns True if placed."""
        candidates = []
        for reel in range(self.config.num_reels - 1):
            for row in range(self.config.num_rows[reel]):
                if self.board[reel][row].name == "S" or self.board[reel + 1][row].name == "S":
                    continue
                candidates.append((reel, row))
        if not candidates:
            return False
        sa_reel, row = random.choice(candidates)
        self.board[sa_reel][row] = self.create_symbol("SA")
        self.board[sa_reel + 1][row] = self.create_symbol("SB")
        self.get_special_symbols_on_board()
        force_pair_event(self, sa_reel, row)
        return True

    def explode_pairs(self, pairs: list) -> None:
        """Mark the union of all current pair blasts, skipping the FS symbol."""
        volatile = self.explosions_are_volatile()
        cells = set()
        for sa_reel, row in pairs:
            cells.update(self.blast_cells_for_pair(sa_reel, row, volatile))

        scatter_cells = {
            (pos["reel"], pos["row"]) for pos in self.special_syms_on_board.get("scatter", [])
        }
        exploding = sorted(cell for cell in cells if cell not in scatter_cells)
        for reel, row in exploding:
            self.board[reel][row].explode = True
        self.protect_scatter_from_explode()

        self.win_data = {
            "totalWin": 0,
            "wins": [
                {
                    "symbol": "SA_SB",
                    "win": 0,
                    "positions": [{"reel": reel, "row": row} for reel, row in exploding],
                    "meta": {"kind": "explosion", "volatile": volatile},
                }
            ],
        }
        explosion_event(self, pairs, exploding, volatile)

    def resolve_board(self) -> None:
        """Pay cascades first, then simultaneous SA+SB blasts, until the board settles."""
        guarantee_pair = (
            self.gametype == self.config.basegame_type
            and self.config.mode_guarantee_pair.get(self.betmode, False)
            and not self.volatile_pair_forced
        )
        steps = 0
        while not self.wincap_triggered and steps < self.config.max_cascade_steps:
            steps += 1
            self.get_scatterpays_update_wins()
            self.emit_tumble_win_events()
            if self.win_data["totalWin"] > 0:
                self.tumble_game_board()
                continue

            if guarantee_pair:
                if not self.find_sa_sb_pairs():
                    self.force_volatile_pair()
                self.volatile_pair_forced = True
                guarantee_pair = False

            pairs = self.find_sa_sb_pairs()
            if not pairs:
                break
            self.explode_pairs(pairs)
            self.tumble_game_board()

        self.set_end_tumble_event()

    def set_end_tumble_event(self) -> None:
        if self.win_manager.spin_win > 0:
            set_win_event(self)
        set_total_event(self)

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Always award a fixed 10 free spins."""
        self.tot_fs = self.config.free_spin_amount
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

    def check_fs_condition(self, scatter_key: str = "scatter") -> bool:
        """FS only from base after settle: S on a bonus cell, or the guaranteed-FS buy."""
        if self.gametype != self.config.basegame_type or self.repeat:
            return False
        if self.config.mode_guarantee_fs.get(self.betmode, False):
            return True
        return self.scatter_on_bonus_area()

    def check_freespin_entry(self, scatter_key: str = "scatter") -> bool:
        """Respect distribution force_freegame flags."""
        if self.get_current_distribution_conditions()["force_freegame"] and self.check_fs_condition():
            return True
        self.repeat = True
        return False
