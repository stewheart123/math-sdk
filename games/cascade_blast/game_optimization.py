"""Stub optimization fences for Cascade Blast. Weights will be retuned after the first book dump."""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructFenceBias,
    ConstructConditions,
    verify_optimization_input,
)


def _base_like_params(wincap: float, include_zero: bool = True) -> dict:
    conditions = {
        "wincap": ConstructConditions(rtp=0.01, av_win=wincap, search_conditions=wincap).return_dict(),
        "freegame": ConstructConditions(
            rtp=0.37, hr=200, search_conditions={"symbol": "scatter"}
        ).return_dict(),
        "basegame": ConstructConditions(hr=3.5, rtp=0.585).return_dict(),
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
                    "scale_factor": 1.2,
                    "win_range": (3000, 4000),
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
            bias_ranges=[(3.0, 5.0)],
            bias_weights=[0.5],
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
                    "win_range": (3000, 4000),
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
            bias_ranges=[(90.0, 150.0)],
            bias_weights=[0.1],
        ).return_dict(),
    }


class OptimizationSetup:
    """Handle all game mode optimization parameters."""

    def __init__(self, game_config):
        self.game_config = game_config
        wincaps = {bm.get_name(): bm.get_wincap() for bm in game_config.bet_modes}
        self.game_config.opt_params = {
            "base": _base_like_params(wincaps["base"]),
            "bonus_hotspots": _base_like_params(wincaps["bonus_hotspots"]),
            "bonus_volatile": _base_like_params(wincaps["bonus_volatile"], include_zero=False),
            "bonus_fs": _fs_buy_params(wincaps["bonus_fs"]),
        }
        verify_optimization_input(self.game_config, self.game_config.opt_params)
