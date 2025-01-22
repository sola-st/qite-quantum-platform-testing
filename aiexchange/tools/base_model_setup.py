import os
from pathlib import Path

import google.generativeai as genai

# Configure Google API
if "GROQ_API_KEY" not in os.environ:
    GEMINI_TOKEN_PATH = Path("gemini_token.txt").resolve()
    GEMINI_TOKEN = GEMINI_TOKEN_PATH.read_text().strip()
    genai.configure(api_key=GEMINI_TOKEN)
    os.environ["GEMINI_API_KEY"] = GEMINI_TOKEN

# Configure Groq API
if "GROQ_API_KEY" not in os.environ:
    GROQ_TOKEN_PATH = Path("groq_token.txt").resolve()
    GROQ_TOKEN = GROQ_TOKEN_PATH.read_text().strip()
    os.environ["GROQ_API_KEY"] = GROQ_TOKEN


# Configure OPENAI API
if "OPENAI_API_KEY" not in os.environ:
    OPENAI_TOKEN_PATH = Path("openai_token.txt").resolve()
    OPENAI_TOKEN = OPENAI_TOKEN_PATH.read_text().strip()
    os.environ["OPENAI_API_KEY"] = OPENAI_TOKEN
