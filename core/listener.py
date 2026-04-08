import asyncio
import numpy as np
import sounddevice as sd
from openwakeword.model import Model
import config

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280  # 80ms at 16kHz — required by openWakeWord


class Listener:
    def __init__(self):
        print("[listener] loading wake word model...")
        self.oww = Model(
            wakeword_models=[config.WAKE_WORD_MODEL],
            inference_framework="onnx"
        )
        print("[listener] ready — say 'Hey Jarwis'")

    async def wait_for_wake_word(self) -> bool:
        """
        Block until the wake word is detected.
        Returns True when detected.
        """
        loop = asyncio.get_event_loop()
        detected = asyncio.Event()

        def audio_callback(indata, frames, time_info, status):
            audio = np.squeeze(indata)
            audio_int16 = (audio * 32768).astype(np.int16)
            scores = self.oww.predict(audio_int16)
            for model_name, score in scores.items():
                if score > config.WAKE_WORD_THRESHOLD:
                    print(f"\n[listener] wake word detected! score={score:.2f}")
                    loop.call_soon_threadsafe(detected.set)

        with sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32",
            blocksize=CHUNK_SIZE,
            callback=audio_callback
        ):
            await detected.wait()

        return True

    async def record_command(self, seconds: int = 5) -> np.ndarray:
        """
        Record audio for the user's command after wake word fires.
        Returns float32 numpy array at 16kHz.
        """
        print("[listener] listening for command...")
        audio = await asyncio.to_thread(
            sd.rec,
            int(seconds * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype="float32"
        )
        await asyncio.to_thread(sd.wait)
        return audio.flatten()
