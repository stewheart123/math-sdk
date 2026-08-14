"""Cascade Blast configuration: 7x7 pay-anywhere cascade with bonus areas and SA+SB blasts."""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Load all game specific parameters and elements."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "cascade_blast"
        self.game_name = "cascade_blast"
        self.provider_number = 0
        self.working_name = "Cascade Blast"
        self.wincap = 5000.0
        self.win_type = "scatter"
        self.rtp = 0.965
        self.construct_paths()

        self.num_reels = 7
        self.num_rows = [7] * self.num_reels

        t1, t2, t3, t4 = (8, 8), (9, 10), (11, 13), (14, 49)
        pay_group = {
            (t1, "H1"): 3.0,
            (t2, "H1"): 7.5,
            (t3, "H1"): 15.0,
            (t4, "H1"): 60.0,
            (t1, "H2"): 2.0,
            (t2, "H2"): 5.0,
            (t3, "H2"): 10.0,
            (t4, "H2"): 40.0,
            (t1, "H3"): 1.3,
            (t2, "H3"): 3.2,
            (t3, "H3"): 7.0,
            (t4, "H3"): 30.0,
            (t1, "H4"): 1.0,
            (t2, "H4"): 2.5,
            (t3, "H4"): 6.0,
            (t4, "H4"): 20.0,
            (t1, "L1"): 0.6,
            (t2, "L1"): 1.5,
            (t3, "L1"): 4.0,
            (t4, "L1"): 10.0,
            (t1, "L2"): 0.4,
            (t2, "L2"): 1.2,
            (t3, "L2"): 3.5,
            (t4, "L2"): 8.0,
            (t1, "L3"): 0.2,
            (t2, "L3"): 0.8,
            (t3, "L3"): 2.5,
            (t4, "L3"): 5.0,
            (t1, "L4"): 0.1,
            (t2, "L4"): 0.5,
            (t3, "L4"): 1.5,
            (t4, "L4"): 4.0,
        }
        self.paytable = self.convert_range_table(pay_group)

        self.include_padding = True
        self.special_symbols = {
            "wild": [],
            "scatter": ["S"],
            "bomb_a": ["SA"],
            "bomb_b": ["SB"],
        }

        self.freespin_triggers = {
            self.basegame_type: {1: 10},
            self.freegame_type: {},
        }
        self.anticipation_triggers = {
            self.basegame_type: 2,
            self.freegame_type: 99,
        }
        self.free_spin_amount = 10
        self.max_cascade_steps = 50

        self.mode_bonus_areas = {
            "base": 1,
            "bonus_hotspots": 5,
            "bonus_volatile": 1,
            "bonus_fs": 1,
        }
        self.mode_volatile_base = {
            "base": False,
            "bonus_hotspots": False,
            "bonus_volatile": True,
            "bonus_fs": False,
        }
        self.mode_guarantee_pair = {
            "base": False,
            "bonus_hotspots": False,
            "bonus_volatile": True,
            "bonus_fs": False,
        }
        self.mode_guarantee_fs = {
            "base": False,
            "bonus_hotspots": False,
            "bonus_volatile": False,
            "bonus_fs": True,
        }

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "WCAP.csv"}
        self.reels = {}
        for reel_id, filename in reels.items():
            self.reels[reel_id] = self.read_reels_csv(os.path.join(self.reels_path, filename))

        self.padding_reels[self.basegame_type] = self.reels["BR0"]
        self.padding_reels[self.freegame_type] = self.reels["FR0"]

        mode_maxwins = {
            "base": 5000,
            "bonus_hotspots": 5000,
            "bonus_volatile": 5000,
            "bonus_fs": 5000,
        }

        base_reel_weights = {
            self.basegame_type: {"BR0": 1},
            self.freegame_type: {"FR0": 1},
        }
        wincap_reel_weights = {
            self.basegame_type: {"BR0": 1},
            self.freegame_type: {"FR0": 1, "WCAP": 5},
        }

        def base_like_distributions(include_zero: bool = True):
            distributions = [
                Distribution(
                    criteria="wincap",
                    quota=0.001,
                    win_criteria=mode_maxwins["base"],
                    conditions={
                        "reel_weights": wincap_reel_weights,
                        "force_wincap": True,
                        "force_freegame": True,
                    },
                ),
                Distribution(
                    criteria="freegame",
                    quota=0.1,
                    conditions={
                        "reel_weights": base_reel_weights,
                        "force_wincap": False,
                        "force_freegame": True,
                    },
                ),
            ]
            if include_zero:
                distributions.append(
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    )
                )
                basegame_quota = 0.5
            else:
                # Guaranteed explosions make true 0-wins vanishingly rare.
                basegame_quota = 0.899
            distributions.append(
                Distribution(
                    criteria="basegame",
                    quota=basegame_quota,
                    conditions={
                        "reel_weights": {self.basegame_type: {"BR0": 1}},
                        "force_wincap": False,
                        "force_freegame": False,
                    },
                )
            )
            return distributions

        def fs_buy_distributions(max_win):
            return [
                Distribution(
                    criteria="wincap",
                    quota=0.001,
                    win_criteria=max_win,
                    conditions={
                        "reel_weights": wincap_reel_weights,
                        "force_wincap": True,
                        "force_freegame": True,
                    },
                ),
                Distribution(
                    criteria="freegame",
                    quota=0.999,
                    conditions={
                        "reel_weights": base_reel_weights,
                        "force_wincap": False,
                        "force_freegame": True,
                    },
                ),
            ]

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=base_like_distributions(),
            ),
            BetMode(
                name="bonus_hotspots",
                cost=5.0,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus_hotspots"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=base_like_distributions(),
            ),
            BetMode(
                name="bonus_volatile",
                cost=10.0,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus_volatile"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=base_like_distributions(include_zero=False),
            ),
            BetMode(
                name="bonus_fs",
                cost=25.0,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus_fs"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=fs_buy_distributions(mode_maxwins["bonus_fs"]),
            ),
        ]
