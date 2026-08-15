"""Cascade Blast configuration: 6x6 pay-anywhere cascade with bonus areas and SA+SB blasts."""

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

        self.num_reels = 6
        self.num_rows = [6] * self.num_reels

        t1, t2, t3, t4 = (8, 8), (9, 10), (11, 13), (14, 36)
        pay_group = {
            (t1, "H1"): 3.5,
            (t2, "H1"): 8.7,
            (t3, "H1"): 20.8,
            (t4, "H1"): 86.0,
            (t1, "H2"): 2.4,
            (t2, "H2"): 6.1,
            (t3, "H2"): 13.8,
            (t4, "H2"): 55.0,
            (t1, "H3"): 1.6,
            (t2, "H3"): 3.8,
            (t3, "H3"): 9.5,
            (t4, "H3"): 38.0,
            (t1, "H4"): 1.2,
            (t2, "H4"): 3.1,
            (t3, "H4"): 6.9,
            (t4, "H4"): 26.0,
            (t1, "L1"): 0.6,
            (t2, "L1"): 1.7,
            (t3, "L1"): 4.8,
            (t4, "L1"): 14.0,
            (t1, "L2"): 0.4,
            (t2, "L2"): 1.2,
            (t3, "L2"): 3.5,
            (t4, "L2"): 10.4,
            (t1, "L3"): 0.2,
            (t2, "L3"): 0.8,
            (t3, "L3"): 2.4,
            (t4, "L3"): 6.9,
            (t1, "L4"): 0.14,
            (t2, "L4"): 0.5,
            (t3, "L4"): 1.7,
            (t4, "L4"): 4.8,
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
            "bonus_volatile": 3,
            "bonus_fs": 1,
        }
        self.mode_volatile_base = {
            "base": False,
            "bonus_hotspots": False,
            "bonus_volatile": True,
            "bonus_fs": False,
        }
        self.mode_min_explosions = {
            "base": 0,
            "bonus_hotspots": 0,
            "bonus_volatile": 3,
            "bonus_fs": 0,
        }
        self.mode_guarantee_fs = {
            "base": False,
            "bonus_hotspots": False,
            "bonus_volatile": False,
            "bonus_fs": True,
        }

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "VR0": "VR0.csv", "WCAP": "WCAP.csv"}
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

        volatile_reel_weights = {
            self.basegame_type: {"VR0": 1},
            self.freegame_type: {"FR0": 1},
        }
        volatile_wincap_reel_weights = {
            self.basegame_type: {"VR0": 1},
            self.freegame_type: {"FR0": 1, "WCAP": 5},
        }

        def base_like_distributions(include_zero: bool = True, reel_weights=None, wincap_weights=None):
            weights = reel_weights or base_reel_weights
            cap_weights = wincap_weights or wincap_reel_weights
            distributions = [
                Distribution(
                    criteria="wincap",
                    quota=0.001,
                    win_criteria=mode_maxwins["base"],
                    conditions={
                        "reel_weights": cap_weights,
                        "force_wincap": True,
                        "force_freegame": True,
                    },
                ),
                Distribution(
                    criteria="freegame",
                    quota=0.1,
                    conditions={
                        "reel_weights": weights,
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
                            "reel_weights": weights,
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
                        "reel_weights": weights,
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
                cost=2.3,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus_hotspots"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=base_like_distributions(),
            ),
            BetMode(
                name="bonus_volatile",
                cost=15.7,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus_volatile"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=base_like_distributions(
                    include_zero=False,
                    reel_weights=volatile_reel_weights,
                    wincap_weights=volatile_wincap_reel_weights,
                ),
            ),
            BetMode(
                name="bonus_fs",
                cost=17.8,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus_fs"],
                auto_close_disabled=False,
                is_feature=False,
                is_buybonus=True,
                distributions=fs_buy_distributions(mode_maxwins["bonus_fs"]),
            ),
        ]
