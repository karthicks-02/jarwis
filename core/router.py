import re
from typing import Optional

# Each entry: (regex_pattern, action_name, param_extractor_fn)
ROUTES = [
    (r"volume\s+(\d+)", "set_volume", lambda m: {"level": m.group(1)}),
    (r"open\s+([a-zA-Z][a-zA-Z0-9\s]+)", "open_app", lambda m: {"app": m.group(1).strip()}),
    (r"battery", "get_battery", lambda m: {}),
    (r"brightness\s+(\d+)", "set_brightness", lambda m: {"level": m.group(1)}),
    (r"\bmute\b", "mute_volume", lambda m: {}),
    (r"what time|time is it|time என்ன|time சொல்", "get_time", lambda m: {}),
    (r"what.*date|today.*date|date என்ன|இன்னைக்கு date", "get_date", lambda m: {}),
    (r"shutdown|close jarwis|stop jarwis|bye jarwis", "shutdown", lambda m: {}),
]

def keyword_route(text: str) -> Optional[tuple[str, dict]]:
    """
    Tier 0 router: match simple command patterns without any LLM call.
    Returns (action_name, params) or None if no pattern matches.
    """
    text_lower = text.lower()
    for pattern, action, extractor in ROUTES:
        match = re.search(pattern, text_lower)
        if match:
            # Also match against original text to preserve casing in extracted params
            original_match = re.search(pattern, text, re.IGNORECASE)
            return action, extractor(original_match if original_match else match)
    return None
