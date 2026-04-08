import pytest
from core.transcriber import Transcriber

def test_transcriber_loads():
    """Verify the Whisper model loads without error."""
    t = Transcriber()
    assert t.model is not None

def test_transcribe_returns_tuple():
    """transcribe() must return (str, str) — text and language."""
    import numpy as np
    t = Transcriber()
    # 1 second of silence — should return empty or near-empty text
    silence = np.zeros(16000, dtype=np.float32)
    text, language = t.transcribe(silence)
    assert isinstance(text, str)
    assert language in ("tamil", "english")

def test_language_is_tamil_or_english():
    """Language output must always be exactly 'tamil' or 'english'."""
    import numpy as np
    t = Transcriber()
    silence = np.zeros(16000, dtype=np.float32)
    _, language = t.transcribe(silence)
    assert language in ("tamil", "english")
