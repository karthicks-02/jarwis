from core.router import keyword_route

def test_volume_match():
    action, params = keyword_route("volume 50")
    assert action == "set_volume"
    assert params["level"] == "50"

def test_volume_in_tamil():
    action, params = keyword_route("volume 70 வை")
    assert action == "set_volume"
    assert params["level"] == "70"

def test_open_app():
    action, params = keyword_route("open Spotify")
    assert action == "open_app"
    assert params["app"] == "Spotify"

def test_battery_check():
    result = keyword_route("battery எவ்வளவு")
    assert result is not None
    action, params = result
    assert action == "get_battery"

def test_no_match_returns_none():
    result = keyword_route("what is the weather in Chennai")
    assert result is None

def test_mute():
    action, _ = keyword_route("mute")
    assert action == "mute_volume"

def test_time():
    action, _ = keyword_route("what time is it")
    assert action == "get_time"

def test_shutdown():
    action, _ = keyword_route("shutdown jarwis")
    assert action == "shutdown"

def test_brightness():
    action, params = keyword_route("brightness 80")
    assert action == "set_brightness"
    assert params["level"] == "80"

def test_case_insensitive():
    action, params = keyword_route("OPEN Safari")
    assert action == "open_app"
    assert params["app"].lower() == "safari"

def test_date():
    action, _ = keyword_route("what is today's date")
    assert action == "get_date"
