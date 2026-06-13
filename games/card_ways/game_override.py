import random

from game_executables import GameExecutables
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """Modifier-area logic and state overrides."""

    def reset_book(self):
        super().reset_book()
        self.modifier_symbol = None
        self.modifier_mult = 1
        self.modifier_reel_id = None
        self.modifier_position = 0
        self.fs_modifier_symbol = None
        self.fs_modifier_mult = 1

    def assign_special_sym_function(self):
        self.special_symbol_functions = {}

    def draw_modifier(self) -> None:
        """Draw one symbol from the modifier reel strip."""
        if self.criteria == "wincap":
            self.modifier_reel_id = "MR0"
            self.modifier_symbol = "X3"
            self.modifier_mult = self.config.modifier_values["X3"]
            self.modifier_position = 0
            return

        conditions = self.get_current_distribution_conditions()
        modifier_weights = conditions.get(
            "modifier_reel_weights",
            {self.gametype: {"MR0": 1}},
        )
        self.modifier_reel_id = get_random_outcome(modifier_weights[self.gametype])
        strip = self.config.modifier_reels[self.modifier_reel_id][0]
        self.modifier_position = random.randrange(len(strip))
        self.modifier_symbol = strip[self.modifier_position]
        self.modifier_mult = self.config.modifier_values[self.modifier_symbol]

    def start_freespin_modifier(self) -> None:
        """Draw modifier once at free-spin entry; persists for the entire feature."""
        self.draw_modifier()
        self.fs_modifier_symbol = self.modifier_symbol
        self.fs_modifier_mult = self.modifier_mult

    def update_final_win(self) -> None:
        """Round wins to 0.1x bet increments for RGS publish format."""
        if self.criteria == "wincap" and self.triggered_freegame:
            self.win_manager.basegame_wins = 0.0
            self.win_manager.freegame_wins = self.config.wincap
            self.win_manager.running_bet_win = self.config.wincap
            self.wincap_triggered = True

        self.win_manager.running_bet_win = round(self.win_manager.running_bet_win, 1)
        self.win_manager.basegame_wins = round(self.win_manager.basegame_wins, 1)
        self.win_manager.freegame_wins = round(self.win_manager.freegame_wins, 1)
        super().update_final_win()

    def check_game_repeat(self):
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and round(self.final_win, 2) != round(win_criteria, 2):
                self.repeat = True
