from game_calculations import GameCalculations
from src.calculations.ways import Ways


class GameExecutables(GameCalculations):
    """Ways wins with post-evaluation modifier multiplier."""

    def apply_modifier_to_win_data(self, modifier_mult: int) -> None:
        """Multiply evaluated ways wins by the active modifier."""
        if modifier_mult == 1 or self.win_data["totalWin"] <= 0:
            return

        self.win_data["totalWin"] = round(self.win_data["totalWin"] * modifier_mult, 1)
        for win in self.win_data["wins"]:
            win["win"] = round(win["win"] * modifier_mult, 1)
            win["meta"]["modifierMult"] = modifier_mult

    def evaluate_ways_board(self, modifier_mult: int = 1):
        """Populate win-data, apply modifier, record wins, transmit events."""
        self.win_data = Ways.get_ways_data(self.config, self.board)
        if self.win_data["totalWin"] > 0:
            self.win_data["totalWin"] = round(self.win_data["totalWin"], 1)
            for win in self.win_data["wins"]:
                win["win"] = round(win["win"], 1)
        self.apply_modifier_to_win_data(modifier_mult)
        if self.win_data["totalWin"] > 0:
            Ways.record_ways_wins(self)
            self.win_manager.update_spinwin(self.win_data["totalWin"])
        Ways.emit_wayswin_events(self)
