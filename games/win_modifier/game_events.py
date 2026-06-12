"""Events for the separate modifier area."""

from src.events.events import json_ready_sym

MODIFIER_REVEAL = "modifierReveal"


def modifier_reveal_event(gamestate, persists: bool = False) -> None:
    """Emit the current modifier symbol drawn from the modifier reel strip."""
    special_attributes = list(gamestate.config.special_symbols.keys())
    modifier_sym = gamestate.create_symbol(gamestate.modifier_symbol)

    event = {
        "index": len(gamestate.book.events),
        "type": MODIFIER_REVEAL,
        "modifier": json_ready_sym(modifier_sym, special_attributes),
        "multiplier": gamestate.modifier_mult,
        "modifierReelId": gamestate.modifier_reel_id,
        "modifierPosition": gamestate.modifier_position,
        "persists": persists,
    }
    event["modifier"]["multiplier"] = gamestate.modifier_mult
    gamestate.book.add_event(event)
