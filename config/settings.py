# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# CHEMINS ABSOLUS DU PROJET
# ==========================================
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"

# ==========================================
# CONFIGURATION DES LLMs
# ==========================================
GEMINI_CONFIG = {
    "text": "gemini-3.6-flash",
    "voice": "gemini-2.5-flash-preview-tts"
}

GROQ_MODELS = [
    "openai/gpt-oss-20b",
    "llama-3.3-70b-specdec"
]

OPENROUTER_ROUTING = [
    "meta-llama/llama-3.3-70b-instruct",
    "google/gemma-3-27b-it:free",
]

# ==========================================
# CLÉS API & SÉCURITÉ
# ==========================================
# Centralisation pour faire crasher l'appli tôt si une clé manque
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")