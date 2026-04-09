import asyncio
import sys

from core.listener import Listener
from core.transcriber import Transcriber
from core.speaker import speak
from core.orchestrator import Orchestrator
from core.registry import load_tools

BOOT_MSG = "Jarwis online. Say Hey Jarvis to begin."
SHUTDOWN_MSG = "Jarwis shutting down. Goodbye."

# Seconds to wait after speaking before listening for wake word again
# Prevents Jarwis from hearing its own voice and re-triggering
POST_SPEAK_COOLDOWN = 1.5


async def main():
    print("=" * 50)
    print("  JARWIS — Personal AI Assistant")
    print("=" * 50)

    tool_map, ollama_schemas, claude_schemas = load_tools()

    listener = Listener()
    transcriber = Transcriber()
    orchestrator = Orchestrator(tool_map, ollama_schemas, claude_schemas)

    await speak(BOOT_MSG, "english")
    await asyncio.sleep(POST_SPEAK_COOLDOWN)
    print("\n[jarwis] listening for 'Hey Jarvis'...\n")

    while True:
        try:
            # Reset OWW state so prior detections don't bleed through
            listener.reset()

            await listener.wait_for_wake_word()

            await speak("Yes?", "english")
            await asyncio.sleep(0.3)  # mic settle time

            audio = await listener.record_command(seconds=5)

            text, language = transcriber.transcribe(audio)
            if not text.strip():
                await speak("I didn't catch that. Try again.", "english")
                await asyncio.sleep(POST_SPEAK_COOLDOWN)
                continue

            print(f"[jarwis] heard ({language}): {text}")

            response = await orchestrator.process(text, language)

            if response == "SHUTDOWN":
                await speak(SHUTDOWN_MSG, "english")
                sys.exit(0)

            print(f"[jarwis] reply: {response}")
            await speak(response, language)
            # Cooldown so Jarwis doesn't hear its own reply
            await asyncio.sleep(POST_SPEAK_COOLDOWN)

        except KeyboardInterrupt:
            await speak(SHUTDOWN_MSG, "english")
            sys.exit(0)
        except Exception as e:
            print(f"[jarwis] error: {e}")
            await speak("Something went wrong. I'm still here.", "english")
            await asyncio.sleep(POST_SPEAK_COOLDOWN)


if __name__ == "__main__":
    asyncio.run(main())
