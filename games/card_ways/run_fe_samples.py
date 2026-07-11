"""Generate a small uncompressed book set for frontend testing."""
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
        "bonus_3": 100,
        "bonus_4": 100,
        "bonus_5": 100,
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
