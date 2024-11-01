import os
from typing import Union

from autogen import AssistantAgent, UserProxyAgent

# Agent Types
AgentType = Union[AssistantAgent, UserProxyAgent]

# File Paths
AGENT_CONFIG_FILE = "agent_config.json"
CSS_FILE = ".css/app_styles.css"
ENV_FILE = ".env"

# Directories
DATA_DIR = "data"
CODING_DIR = "coding"

# Model Providers
MODEL_PROVIDER_OPENAI = "OpenAI"
MODEL_PROVIDER_OLLAMA = "Ollama"
MODEL_PROVIDER_HUGGINGFACE = "HuggingFace"

# OpenAI Models
OPENAI_MODEL_GPT4O_MINI = "gpt-4o-mini"
OPENAI_MODEL_GPT4O = "gpt-4o"
OPENAI_MODEL_O1_MINI = "o1-mini"
OPENAI_MODEL_O1_PREVIEW = "o1-preview"

# Ollama Models
OLLAMA_MODEL_LLAMA31 = "llama3.1"

# HuggingFace Models
HUGGINGFACE_MODEL_META_LLAMA_70B = "meta-llama/Meta-Llama-3-70B"
HUGGINGFACE_MODEL_MIXTRAL = "mistralai/Mixtral-8x7B-v0.1"
HUGGINGFACE_MODEL_GEMMA = "google/gemma-2-9b"
HUGGINGFACE_MODEL_META_LLAMA_405B = "meta-llama/Meta-Llama-3.1-405B-Instruct"

# API Configuration
OLLAMA_BASE_URL = "http://0.0.0.0:4000"
OLLAMA_API_KEY = "NULL"

# File Extensions
SRT_EXTENSION = ".srt"

# Encoding
UTF8_ENCODING = "utf-8"

# Special Characters
BYTE_ORDER_MARK = "\ufeff"

# Subtitle Formatting
MAX_SUBTITLE_LINES = 2
MAX_SUBTITLE_LINE_LENGTH = 50

# Wiktionary
MAX_DEFINITIONS = 20

# Chunk Sizes
DEFAULT_SUBTITLE_CHUNK_SIZE = 30

# Messages
TERMINATION_MESSAGE = "TERMINATE"
FORMATTED_SUBTITLES_START = "FORMATTED_SUBTITLES:"
FORMATTED_SUBTITLES_END = "END_OF_SUBTITLES"

# Languages
LANGUAGE_ENGLISH = "English"
LANGUAGE_FRENCH = "French"
LANGUAGE_GERMAN = "German"
LANGUAGE_ITALIAN = "Italian"
LANGUAGE_SPANISH = "Spanish"
LANGUAGE_TURKISH = "Turkish"

# Logging
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

# Version
with open(os.path.join(os.path.dirname(__file__), "VERSION")) as version_file:
    APP_VERSION = version_file.read().strip()
