"""Generate a small uncompressed book set for frontend testing.

Warning: this overwrites library/books and rebuilds LUTs from 100 sims.
Prefer export_fe_maths.py against existing 10k books unless you need a fresh run.
"""
from gamestate import GameState
from game_config import GameConfig
from src.state.run_sims import create_books
from src.write_data.write_configs import generate_configs

if __name__ == "__main__":
    num_threads = 1
    batching_size = 50000
    compression = False
    profiling = False

    num_sim_args = {
        "base": 100,
        "bonus_hotspots": 100,
        "bonus_volatile": 100,
        "bonus_fs": 100,
    }

    config = GameConfig()
    config.output_regular_json = False
    gamestate = GameState(config)

    create_books(
        gamestate,
        config,
        num_sim_args,
        batching_size,
        num_threads,
        compression,
        profiling,
    )

    generate_configs(gamestate)
    print("FE sample books written to library/books/")
