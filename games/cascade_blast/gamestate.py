"""Gamestate for a single Cascade Blast spin."""

from game_override import GameStateOverride


class GameState(GameStateOverride):
    """Pay-anywhere cascade with bonus-area FS trigger and SA+SB explosions."""

    def run_spin(self, sim: int, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_and_resolve_base()
            self.win_manager.update_gametype_wins(self.gametype)

            if (
                self.betmode != "bonus_fs"
                and self.get_current_distribution_conditions().get("force_freegame")
            ):
                self.ensure_scatter_on_bonus_area()

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs and not self.wincap_triggered:
            self.update_freespin()
            self.draw_board()
            self.resolve_board()
            self.win_manager.update_gametype_wins(self.gametype)
        self.end_freespin()
