import asyncio
import os
import tempfile
import edge_tts
import pygame
import config

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)


async def speak(text: str, language: str = "english") -> None:
    if not text or not text.strip():
        return

    voice = config.TTS_TAMIL_VOICE if language == "tamil" else config.TTS_ENGLISH_VOICE

    # Use a unique temp file each time to avoid stale file conflicts
    fd, output_file = tempfile.mkstemp(suffix=".mp3", prefix="jarwis_")
    os.close(fd)

    try:
        for attempt in range(3):
            try:
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_file)
                if os.path.getsize(output_file) > 0:
                    break
            except Exception as e:
                if attempt == 2:
                    print(f"[speaker] TTS failed after 3 attempts: {e}")
                    return
                await asyncio.sleep(1)
        else:
            print("[speaker] TTS produced empty file, skipping")
            return

        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)

    finally:
        try:
            os.remove(output_file)
        except OSError:
            pass
