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

    def check_game_repeat(self):
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True
