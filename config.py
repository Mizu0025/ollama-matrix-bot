import os
import sys
import logging

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("OllamaBot")

# --- Environment Variables ---
MATRIX_URL = os.getenv("MATRIX_URL")
MATRIX_ID = os.getenv("MATRIX_ID")
MATRIX_TOKEN = os.getenv("MATRIX_TOKEN")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434").rstrip("/")
COMFYUI_URL = os.getenv("COMFYUI_URL", "http://localhost:8000").rstrip("/")
DATA_FILE = os.getenv("DATA_FILE", "/app/store/bot_data.json")
SESSION_FILE = os.getenv("SESSION_FILE", "/app/store/session.txt")

# --- Defaults ---
DEFAULT_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:12b")

SYSTEM_INSTRUCTION = (
    "You are a helpful software assistant. "
    "You have access to the local filesystem in the container. "
    "If the user asks about directories or files, you can check them using Python if needed, "
    "but for now, simply report what you see if you are asked to 'check' something."
)
