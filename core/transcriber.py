import warnings
from faster_whisper import WhisperModel
import numpy as np
import sounddevice as sd
import config

warnings.filterwarnings("ignore", category=RuntimeWarning, module="faster_whisper")

SAMPLE_RATE = 16000
RECORD_SECONDS = 5
# RMS threshold below which audio is treated as silence (no speech)
SILENCE_THRESHOLD = 0.01


class Transcriber:
    def __init__(self):
        print(f"[transcriber] loading Whisper {config.WHISPER_MODEL} model...")
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

    def transcribe(self, audio: np.ndarray) -> tuple:
        """
        Transcribe audio array to text.

        Returns:
            (text, language) where language is 'tamil' or 'english'
            Returns ("", "english") if audio is silence/noise.
        """
        # Drop silent audio to avoid Whisper hallucinations
        rms = float(np.sqrt(np.mean(audio ** 2)))
        if rms < SILENCE_THRESHOLD:
            return "", "english"

        segments, info = self.model.transcribe(
            audio,
            beam_size=1,       # faster, still accurate for short commands
            language=None,     # auto-detect Tamil/English
            task="transcribe",
            vad_filter=True,   # built-in VAD — skips silent regions
            vad_parameters={"min_silence_duration_ms": 500},
            no_speech_threshold=0.6,  # discard low-confidence segments
        )
        text = " ".join(s.text.strip() for s in segments).strip()
        detected = info.language  # e.g. "ta", "en"

        language = "tamil" if detected == "ta" else "english"
        return text, language
