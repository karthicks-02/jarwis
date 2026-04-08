from faster_whisper import WhisperModel
import numpy as np
import sounddevice as sd
import config

SAMPLE_RATE = 16000
RECORD_SECONDS = 5

class Transcriber:
    def __init__(self):
        print("[transcriber] loading Whisper model (first run downloads ~1.5GB)...")
        self.model = WhisperModel(
            config.WHISPER_MODEL,
            device="auto",
            compute_type="int8"
        )
        print("[transcriber] model ready")

    def record_audio(self, seconds: int = RECORD_SECONDS) -> np.ndarray:
        """Record audio from the microphone for `seconds` duration."""
        audio = sd.rec(
            int(seconds * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )
        sd.wait()
        return audio.flatten()

    def transcribe(self, audio: np.ndarray) -> tuple[str, str]:
        """
        Transcribe audio array to text.

        Args:
            audio: float32 numpy array at 16kHz sample rate

        Returns:
            (text, language) where language is 'tamil' or 'english'
        """
        segments, info = self.model.transcribe(
            audio,
            beam_size=5,
            language=None,   # auto-detect
            task="transcribe"
        )
        text = " ".join(s.text.strip() for s in segments).strip()
        detected = info.language  # e.g. "ta", "en", "hi"

        language = "tamil" if detected == "ta" else "english"
        return text, language
