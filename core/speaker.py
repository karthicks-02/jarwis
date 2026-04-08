import asyncio
import edge_tts
import pygame
import os
import config

pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)


async def speak(text: str, language: str = "english") -> None:
    """
    Convert text to speech and play it through speakers.

    Args:
        text: The text to speak
        language: 'tamil' or 'english' (default). Selects appropriate neural voice.
    """
    voice = config.TTS_TAMIL_VOICE if language == "tamil" else config.TTS_ENGLISH_VOICE
    output_file = config.TTS_OUTPUT_FILE

    for attempt in range(3):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_file)
            break
        except Exception as e:
            if attempt == 2:
                raise
            await asyncio.sleep(1)

    pygame.mixer.music.load(output_file)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    try:
        os.remove(output_file)
    except FileNotFoundError:
        pass
