"""Game logic for ways game with separate modifier area."""

from game_events import modifier_reveal_event
from game_override import GameStateOverride


class GameState(GameStateOverride):
    """Handle basegame and freegame logic."""

    def run_spin(self, sim: int, simulation_seed=None) -> None:
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board(emit_event=True)

            self.draw_modifier()
            modifier_reveal_event(self, persists=False)

            self.evaluate_ways_board(modifier_mult=self.modifier_mult)

            self.win_manager.update_gametype_wins(self.gametype)
            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self) -> None:
        self.reset_fs_spin()
        self.start_freespin_modifier()
        modifier_reveal_event(self, persists=True)

        while self.fs < self.tot_fs:
            self.update_freespin()
            self.draw_board(emit_event=True)

            self.evaluate_ways_board(modifier_mult=self.fs_modifier_mult)

            self.win_manager.update_gametype_wins(self.gametype)

        self.end_freespin()
