import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Game specific configuration class."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "win_modifier"
        self.provider_number = 0
        self.working_name = "Win Modifier"
        self.wincap = 5000
        self.win_type = "ways"
        self.rtp = 0.97
        self.construct_paths()

        self.num_reels = 5
        self.num_rows = [2] * self.num_reels

        self.paytable = {
            (5, "A"): 10,
            (4, "A"): 5,
            (3, "A"): 2,
            (5, "K"): 8,
            (4, "K"): 4,
            (3, "K"): 1.5,
            (5, "Q"): 6,
            (4, "Q"): 3,
            (3, "Q"): 1.2,
            (5, "J"): 5,
            (4, "J"): 2.5,
            (3, "J"): 1,
            (5, "10"): 4,
            (4, "10"): 2,
            (3, "10"): 0.8,
            (5, "9"): 3,
            (4, "9"): 1.5,
            (3, "9"): 0.6,
            (5, "8"): 2,
            (4, "8"): 1,
            (3, "8"): 0.4,
        }

        self.include_padding = True
        self.special_symbols = {
            "wild": ["W"],
            "scatter": ["S"],
            "modifier": ["X1", "X2", "X3"],
        }

        self.modifier_values = {"X1": 1, "X2": 2, "X3": 3}
        self.num_modifier_slots = 1

        self.freespin_triggers = {
            self.basegame_type: {3: 10, 4: 10, 5: 10},
            self.freegame_type: {},
        }
        self.anticipation_triggers = {self.basegame_type: 2, self.freegame_type: 0}

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "FRWCAP": "FRWCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))

        self.modifier_reels = {
            "MR0": self.read_reels_csv(os.path.join(self.reels_path, "MR0.csv"))
        }

        modifier_reel_weights = {
            self.basegame_type: {"MR0": 1},
            self.freegame_type: {"MR0": 1},
        }

        mode_maxwins = {"base": 5000, "bonus": 5000}

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=0.101,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "modifier_reel_weights": modifier_reel_weights,
                            "force_wincap": False,
                            "force_freegame": True,
                            "scatter_triggers": {3: 100, 4: 20, 5: 5},
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "modifier_reel_weights": modifier_reel_weights,
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.499,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "modifier_reel_weights": modifier_reel_weights,
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="freegame",
                        quota=1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "FRWCAP": 5},
                            },
                            "modifier_reel_weights": modifier_reel_weights,
                            "force_wincap": False,
                            "force_freegame": True,
                            "scatter_triggers": {3: 100, 4: 20, 5: 5},
                        },
                    ),
                ],
            ),
        ]
