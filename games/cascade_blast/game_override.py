"""State overrides for Cascade Blast."""

from game_executables import GameExecutables


class GameStateOverride(GameExecutables):
    """Reset local state and clamp forced wincap books."""

    def reset_book(self):
        super().reset_book()
        self.tumble_win = 0
        self.bonus_areas = []
        self.bonus_area_set = set()
        self.volatile_pair_forced = False

    def assign_special_sym_function(self):
        self.special_symbol_functions = {}

    def update_final_win(self) -> None:
        """Forced max-win books always publish the cap once FS has been entered."""
        if self.criteria == "wincap" and self.triggered_freegame:
            self.win_manager.basegame_wins = 0.0
            self.win_manager.freegame_wins = self.config.wincap
            self.win_manager.running_bet_win = self.config.wincap
            self.wincap_triggered = True
        super().update_final_win()
