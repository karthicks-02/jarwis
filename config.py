import os
import pathlib
from dotenv import load_dotenv

load_dotenv()

_BASE = pathlib.Path(__file__).parent

# Wake word
WAKE_WORD_MODEL = "hey_jarvis"
WAKE_WORD_THRESHOLD = 0.5

# STT
WHISPER_MODEL = "large-v3"

# Models
OLLAMA_MODEL = "qwen2.5:72b"
CLAUDE_HAIKU_MODEL = "claude-haiku-4-5-20251001"
CLAUDE_SONNET_MODEL = "claude-sonnet-4-6"

# TTS
TTS_TAMIL_VOICE = "ta-IN-ValluvarNeural"
TTS_ENGLISH_VOICE = "en-US-AndrewNeural"
TTS_OUTPUT_FILE = "/tmp/jarwis_reply.mp3"

# Memory
DB_PATH = str(_BASE / "data" / "jarwis.db")
MEMORY_TOP_K = 3

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
CLICKUP_API_TOKEN = os.getenv("CLICKUP_API_TOKEN")
JENKINS_URL = os.getenv("JENKINS_URL", "")
JENKINS_USER = os.getenv("JENKINS_USER", "")
JENKINS_TOKEN = os.getenv("JENKINS_TOKEN", "")
