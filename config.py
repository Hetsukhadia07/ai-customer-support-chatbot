import os
from dotenv import load_dotenv

load_dotenv()

# Application Settings
APP_NAME = "AI Customer Support Chatbot"
APP_VERSION = "1.0.0"
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", 8000))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# Database Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")

# Hugging Face Configuration
HUGGING_FACE_API_KEY = os.getenv("HUGGING_FACE_API_KEY", "")
MODEL_NAME = os.getenv("MODEL_NAME", "mistralai/Mistral-7B-Instruct-v0.1")
MODEL_TEMPERATURE = float(os.getenv("MODEL_TEMPERATURE", 0.7))
MODEL_MAX_TOKENS = int(os.getenv("MODEL_MAX_TOKENS", 512))

# Memory Configuration
MEMORY_TYPE = os.getenv("MEMORY_TYPE", "conversation_buffer")  # Options: conversation_buffer, summary
MAX_CONVERSATION_HISTORY = int(os.getenv("MAX_CONVERSATION_HISTORY", 10))
CONVERSATION_SUMMARY_THRESHOLD = int(os.getenv("CONVERSATION_SUMMARY_THRESHOLD", 20))

# Chatbot System Prompt
SYSTEM_PROMPT = """You are a helpful and professional customer support assistant. 
Your role is to:
1. Listen carefully to customer issues
2. Provide accurate and helpful solutions
3. Maintain a friendly and professional tone
4. Remember previous conversations with the customer
5. Escalate to human support when necessary

Always be empathetic and try to resolve issues quickly and efficiently."""

# CORS Settings
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
