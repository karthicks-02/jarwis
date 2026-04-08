import asyncio
import sys

from core.listener import Listener
from core.transcriber import Transcriber
from core.speaker import speak
from core.orchestrator import Orchestrator
from core.registry import load_tools

BOOT_MSG = "Jarwis online. Say Hey Jarwis to begin."
SHUTDOWN_MSG = "Jarwis shutting down. Goodbye."

async def main():
    print("=" * 50)
    print("  JARWIS — Personal AI Assistant")
    print("=" * 50)

    # Load all tools from tools/ directory
    tool_map, ollama_schemas, claude_schemas = load_tools()

    # Initialize core components
    listener = Listener()
    transcriber = Transcriber()
    orchestrator = Orchestrator(tool_map, ollama_schemas, claude_schemas)

    # Boot announcement
    await speak(BOOT_MSG, "english")
    print("\n[jarwis] listening for 'Hey Jarwis'...\n")

    while True:
        try:
            # Wait for wake word
            await listener.wait_for_wake_word()

            # Acknowledge
            await speak("Yes?", "english")

            # Record command
            audio = await listener.record_command(seconds=5)

            # Transcribe
            text, language = transcriber.transcribe(audio)
            if not text.strip():
                await speak("I didn't catch that. Try again.", "english")
                continue

            print(f"[jarwis] heard ({language}): {text}")

            # Process through 3-tier orchestrator
            response = await orchestrator.process(text, language)

            # Handle shutdown command
            if response == "SHUTDOWN":
                await speak(SHUTDOWN_MSG, "english")
                sys.exit(0)

            print(f"[jarwis] reply: {response}")

            # Speak response in detected language
            await speak(response, language)

        except KeyboardInterrupt:
            await speak(SHUTDOWN_MSG, "english")
            sys.exit(0)
        except Exception as e:
            print(f"[jarwis] error: {e}")
            await speak("Something went wrong. I'm still here.", "english")

if __name__ == "__main__":
    asyncio.run(main())
