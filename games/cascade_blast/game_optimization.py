"""Optimization fences for Cascade Blast, sized from the 4k natural probe."""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructFenceBias,
    ConstructConditions,
    verify_optimization_input,
)


def _mixed_mode_params(
    wincap: float,
    include_zero: bool,
    fs_rtp: float,
    fs_hr: float,
    base_rtp: float,
    base_hr: float,
    fs_win_range: tuple,
    base_bias_range: tuple,
) -> dict:
    conditions = {
        "wincap": ConstructConditions(rtp=0.01, av_win=wincap, search_conditions=wincap).return_dict(),
        "freegame": ConstructConditions(
            rtp=fs_rtp, hr=fs_hr, search_conditions={"symbol": "scatter"}
        ).return_dict(),
        "basegame": ConstructConditions(hr=base_hr, rtp=base_rtp).return_dict(),
    }
    if include_zero:
        conditions["0"] = ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict()
    return {
        "conditions": conditions,
        "scaling": ConstructScaling(
            [
                {
                    "criteria": "basegame",
                    "scale_factor": 1.2,
                    "win_range": (1, 2),
                    "probability": 1.0,
                },
                {
                    "criteria": "freegame",
                    "scale_factor": 1.1,
                    "win_range": fs_win_range,
                    "probability": 1.0,
                },
            ]
        ).return_dict(),
        "parameters": ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[50, 100, 200],
            test_weights=[0.3, 0.4, 0.3],
            score_type="rtp",
            max_trial_dist=15,
        ).return_dict(),
        "distribution_bias": ConstructFenceBias(
            applied_criteria=["basegame"],
            bias_ranges=[base_bias_range],
            bias_weights=[0.4],
        ).return_dict(),
    }


def _fs_buy_params(wincap: float) -> dict:
    return {
        "conditions": {
            "wincap": ConstructConditions(rtp=0.01, av_win=wincap, search_conditions=wincap).return_dict(),
            "freegame": ConstructConditions(rtp=0.955, hr="x").return_dict(),
        },
        "scaling": ConstructScaling(
            [
                {
                    "criteria": "freegame",
                    "scale_factor": 1.2,
                    "win_range": (20, 40),
                    "probability": 1.0,
                },
            ]
        ).return_dict(),
        "parameters": ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[10, 20, 50],
            test_weights=[0.6, 0.2, 0.2],
            score_type="rtp",
            max_trial_dist=15,
        ).return_dict(),
        "distribution_bias": ConstructFenceBias(
            applied_criteria=["freegame"],
            bias_ranges=[(12.0, 22.0)],
            bias_weights=[0.3],
        ).return_dict(),
    }


class OptimizationSetup:
    """Handle all game mode optimization parameters."""

    def __init__(self, game_config):
        self.game_config = game_config
        wincaps = {bm.get_name(): bm.get_wincap() for bm in game_config.bet_modes}
        self.game_config.opt_params = {
            "base": _mixed_mode_params(
                wincap=wincaps["base"],
                include_zero=True,
                fs_rtp=0.295,
                fs_hr=55,
                base_rtp=0.66,
                base_hr=3.5,
                fs_win_range=(10, 25),
                base_bias_range=(0.5, 2.0),
            ),
            "bonus_hotspots": _mixed_mode_params(
                wincap=wincaps["bonus_hotspots"],
                include_zero=True,
                fs_rtp=0.67,
                fs_hr=10,
                base_rtp=0.285,
                base_hr=1.8,
                fs_win_range=(10, 25),
                base_bias_range=(0.5, 2.0),
            ),
            "bonus_volatile": _mixed_mode_params(
                wincap=wincaps["bonus_volatile"],
                include_zero=False,
                fs_rtp=0.08,
                fs_hr=16,
                base_rtp=0.875,
                base_hr=1.05,
                fs_win_range=(20, 45),
                base_bias_range=(8.0, 20.0),
            ),
            "bonus_fs": _fs_buy_params(wincaps["bonus_fs"]),
        }
        verify_optimization_input(self.game_config, self.game_config.opt_params)
