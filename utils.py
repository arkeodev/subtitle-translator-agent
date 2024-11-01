# utils.py

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests
import streamlit as st
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from constants import (
    BYTE_ORDER_MARK,
    CSS_FILE,
    DATA_DIR,
    DEFAULT_SUBTITLE_CHUNK_SIZE,
    ENV_FILE,
    LOG_FORMAT,
    MAX_SUBTITLE_LINE_LENGTH,
    MAX_SUBTITLE_LINES,
    UTF8_ENCODING,
)


def load_css():
    """Load custom CSS styles from a file and apply them to the Streamlit application."""
    css_file = Path(CSS_FILE)
    if css_file.exists():
        with css_file.open("r", encoding=UTF8_ENCODING) as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        logging.warning("CSS file not found.")


def termination_msg(x: Any) -> bool:
    logging.info("Checking for termination message")
    return isinstance(x, dict) and str(x.get("content", "")).strip().upper().endswith(
        "TERMINATE"
    )


def set_api_keys(env_file_path: str = ENV_FILE):
    """Loads and sets necessary API keys for OpenAI."""
    logging.info("Attempting to load API keys from specified .env file.")
    load_dotenv(env_file_path)

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        logging.info("OpenAI API key loaded successfully.")
    else:
        logging.error("OpenAI API key not found in .env file.")


def setup_logging():
    """Sets up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[logging.StreamHandler()],
    )
    logging.info("Logging setup complete")


def save_uploaded_file(uploaded_file: Any, suffix: str = "") -> str:
    """Saves an uploaded file to the specified directory and returns the path."""
    file_name = uploaded_file.name
    name, ext = os.path.splitext(file_name)
    new_name = f"{name}{suffix}{ext}"
    file_path = os.path.join(DATA_DIR, new_name)
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def read_srt_file(file_path: str) -> str:
    """
    Reads the content of an SRT file and returns it as a string.
    """
    try:
        file_path = Path(file_path)
        logging.info(f"Reading SRT file: {file_path}")

        with file_path.open("r", encoding=UTF8_ENCODING) as file:
            content = file.read()

        logging.info(f"Successfully read SRT file: {file_path}")
        return content
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {str(e)}")
        raise


def calculate_subtitle_stats(
    original_content: str, translated_content: str
) -> List[str]:
    """Calculate and report issues in the translated subtitles compared to the original subtitles."""
    original_subs = original_content.strip().split("\n\n")
    translated_subs = translated_content.strip().split("\n\n")
    issues = []

    if len(original_subs) != len(translated_subs):
        issues.append(
            f"Mismatch in number of subtitles: Original has {len(original_subs)}, Translated has {len(translated_subs)}"
        )

    for i, (orig, trans) in enumerate(zip(original_subs, translated_subs), 1):
        orig_lines = orig.strip().split("\n")
        trans_lines = trans.strip().split("\n")

        # Check if subtitle index matches (ignoring extra spaces)
        if orig_lines[0].strip() != trans_lines[0].strip():
            issues.append(
                f"Subtitle {i}: Index mismatch (Original: {orig_lines[0]}, Translated: {trans_lines[0]})"
            )

        # Check if timestamps match (ignoring extra spaces)
        if len(orig_lines) > 1 and len(trans_lines) > 1:
            if orig_lines[1].strip() != trans_lines[1].strip():
                issues.append(
                    f"Subtitle {i}: Timestamp mismatch (Original: {orig_lines[1]}, Translated: {trans_lines[1]})"
                )

        # Extract the text lines from the original and translated subtitles
        orig_text_lines = orig_lines[2:]
        trans_text_lines = trans_lines[2:]

        # Check if the number of lines in the text part matches
        if len(orig_text_lines) != len(trans_text_lines):
            issues.append(f"Subtitle {i}: Line count mismatch")

        # Check if any line in the translated text exceeds MAX_SUBTITLE_LINE_LENGTH characters
        for j, line in enumerate(trans_text_lines, 1):
            if len(line.strip()) > MAX_SUBTITLE_LINE_LENGTH:
                issues.append(
                    f"Subtitle {i}, Line {j}: Exceeds {MAX_SUBTITLE_LINE_LENGTH} characters ({len(line.strip())})"
                )

    return issues


def load_subtitle_file(file_path: str) -> Optional[str]:
    """Loads and validates an SRT file."""
    if file_path and file_path.lower().endswith(".srt"):
        try:
            with open(file_path, "r", encoding=UTF8_ENCODING) as file:
                content = file.read()
            return content
        except Exception as e:
            logging.error(f"Error loading file: {str(e)}")
            return None
    else:
        logging.error("Please select a valid SRT file.")
        return None


def remove_byte_order_mark(content: str) -> str:
    """Remove the Byte Order Mark (BOM) if it exists at the beginning of the content."""
    return content.lstrip(BYTE_ORDER_MARK)


def ensure_byte_order_mark(content: str) -> str:
    """Add the Byte Order Mark (BOM) if it doesn't exist at the beginning of the content."""
    if not content.startswith(BYTE_ORDER_MARK):
        return BYTE_ORDER_MARK + content
    return content


def split_subtitles(
    srt_content: str, chunk_size: int = DEFAULT_SUBTITLE_CHUNK_SIZE
) -> List[str]:
    """Split the loaded SRT file into chunks of specified size."""
    logging.info(f"Splitting subtitles with chunk size: {chunk_size}")
    chunks = []
    current_chunk = ""
    index = 0
    # Remove any leading/trailing whitespace and BOM character
    subtitles = srt_content.strip().strip(BYTE_ORDER_MARK).split("\n\n")
    last_index = len(subtitles)
    # Split the subtitles into chunks of the specified size
    for subtitle in subtitles:
        current_chunk += subtitle + "\n\n"
        index += 1
        if index % chunk_size == 0 or index == last_index:
            chunks.append(current_chunk)
            current_chunk = ""
    logging.info(f"Number of chunks: {len(chunks)}")
    return chunks


def merge_subtitles(translated_chunks: List[str]) -> str:
    """Merge the translated subtitle chunks."""
    logging.info("Merging translated subtitle chunks")
    merged_content = ""
    for chunk in translated_chunks:
        if chunk:
            merged_content += chunk.strip() + "\n\n"
    # Prepend BOM character
    merged_content = BYTE_ORDER_MARK + merged_content.strip()
    logging.info(f"Merged content length: {len(merged_content)} characters")
    return merged_content
