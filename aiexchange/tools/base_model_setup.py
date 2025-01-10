import os
from pathlib import Path

import google.generativeai as genai
from sentence_transformers import SentenceTransformer

# Configure Google API
GEMINI_TOKEN_PATH = Path("gemini_token.txt").resolve()
GEMINI_TOKEN = GEMINI_TOKEN_PATH.read_text().strip()
genai.configure(api_key=GEMINI_TOKEN)
os.environ["GEMINI_API_KEY"] = GEMINI_TOKEN

# Configure Groq API
GROQ_TOKEN_PATH = Path("groq_token.txt").resolve()
GROQ_TOKEN = GROQ_TOKEN_PATH.read_text().strip()
os.environ["GROQ_API_KEY"] = GROQ_TOKEN

# Configure DSPY Models
BASE_MODEL = 'groq/llama-3.1-70b-versatile'
LARGE_CONTEXT_MODEL = 'gemini/gemini-1.5-flash'

# Load a pretrained Sentence Transformer model
EMBEDDING_MODEL = SentenceTransformer("multi-qa-mpnet-base-cos-v1")
