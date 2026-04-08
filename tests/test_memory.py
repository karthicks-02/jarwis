import pytest
import os
import tempfile
from core.memory import Memory

@pytest.fixture
def mem():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    m = Memory(db_path)
    yield m
    os.unlink(db_path)

def test_save_and_get_fact(mem):
    mem.save_fact("User lives in Chennai")
    facts = mem.get_top_facts("Chennai", k=3)
    assert any("Chennai" in f for f in facts)

def test_save_conversation(mem):
    mem.save_conversation("weather?", "It is 34C", "english")
    history = mem.get_recent_conversations(limit=5)
    assert len(history) == 1
    assert history[0]["user_text"] == "weather?"

def test_set_and_get_profile(mem):
    mem.set_profile("name", "Karthick")
    assert mem.get_profile("name") == "Karthick"

def test_get_top_facts_empty(mem):
    facts = mem.get_top_facts("nothing here", k=3)
    assert facts == []

def test_get_top_facts_relevance(mem):
    mem.save_fact("User is from Chennai")
    mem.save_fact("User likes cricket")
    mem.save_fact("User works in software")
    facts = mem.get_top_facts("cricket scores", k=2)
    assert any("cricket" in f.lower() for f in facts)

def test_profile_overwrite(mem):
    mem.set_profile("city", "Chennai")
    mem.set_profile("city", "Mumbai")
    assert mem.get_profile("city") == "Mumbai"
