# subtitle_utils.py

import logging
import re
from typing import Dict, List

import requests
from typing_extensions import Annotated

from agent_models import (
    AlignmentResult,
    FormattingResult,
    WiktionaryDefinition,
    WiktionaryResult,
)
from constants import MAX_DEFINITIONS


def parse_srt(
    srt_content: Annotated[str, "SRT content as a string"]
) -> List[Dict[str, str]]:
    subtitles = []
    for block in srt_content.strip().split("\n\n"):
        lines = block.split("\n")
        index = int(lines[0])
        start_time, end_time = lines[1].split(" --> ")
        text = "\n".join(lines[2:])
        subtitles.append(
            {
                "index": index,
                "start_time": start_time,
                "end_time": end_time,
                "text": text,
            }
        )
    return subtitles


def verify_alignment(
    original_srt: List[Dict[str, str]], formatted_srt: List[Dict[str, str]]
) -> AlignmentResult:
    logging.info(f"Verifying alignment of timestamps of subtitles")
    original_subtitles = parse_srt(original_srt)
    formatted_subtitles = parse_srt(formatted_srt)
    misaligned_indices = []
    for i, (orig, fmt) in enumerate(zip(original_subtitles, formatted_subtitles)):
        if (
            orig["index"] != fmt["index"]
            or orig["start_time"] != fmt["start_time"]
            or orig["end_time"] != fmt["end_time"]
        ):
            misaligned_indices.append(i)

    is_aligned = len(misaligned_indices) == 0
    logging.info(f"Alignment check for {len(original_srt)} subtitles: {is_aligned}")
    return AlignmentResult(is_aligned=is_aligned, misaligned_indices=misaligned_indices)


def format_subtitles(
    reviewed_srt: Annotated[str, "Reviewed SRT content as a string"]
) -> FormattingResult:
    subtitles = parse_srt(reviewed_srt)

    formatted_srt = []
    warnings = []

    for subtitle in subtitles:
        start_time = subtitle["start_time"]
        end_time = subtitle["end_time"]

        text = subtitle["text"]
        lines = []
        current_line = ""
        for word in text.split():
            if len(current_line) + len(word) + 1 <= 50:
                current_line += " " + word if current_line else word
            else:
                lines.append(current_line)
                current_line = word
                if len(lines) == 2:
                    break
        if current_line:
            lines.append(current_line)

        formatted_text = "\n".join(lines)

        formatted_srt.append(
            {
                "index": subtitle["index"],
                "start_time": start_time,
                "end_time": end_time,
                "text": formatted_text,
            }
        )

    for subtitle in formatted_srt:
        lines = subtitle["text"].split("\n")
        if len(lines) > 2:
            warnings.append(
                f"Subtitle {subtitle['index']} has more than 2 lines: {subtitle['text']}"
            )
        for line in lines:
            if len(line) > 50:
                warnings.append(
                    f"Subtitle {subtitle['index']} has a line longer than 50 characters: {line}"
                )

    result = FormattingResult(
        total_subtitles=len(formatted_srt),
        first_subtitle=formatted_srt[0],
        last_subtitle=formatted_srt[-1],
        warnings=warnings,
    )

    logging.info(f"Formatted {result.total_subtitles} subtitles")
    logging.info(f"First subtitle: {result.first_subtitle}")
    logging.info(f"Last subtitle: {result.last_subtitle}")

    for warning in result.warnings:
        logging.warning(warning)

    return result


def get_wiktionary_definition(
    words: List[str],
    language: str = "en",
    max_attempts: int = 1,
    max_definitions: int = MAX_DEFINITIONS,
) -> WiktionaryResult:
    base_url = "https://en.wiktionary.org/api/rest_v1/page/definition/"
    result = WiktionaryResult()

    for word in words[:max_definitions]:
        url = base_url + word

        for _ in range(max_attempts):
            try:
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()

                if language in data:
                    for entry in data[language]:
                        if "definitions" in entry and entry["definitions"]:
                            definition = entry["definitions"][0]["definition"]
                            result.definitions.append(
                                WiktionaryDefinition(
                                    word=word,
                                    definition=clean_definition(definition),
                                    language=language,
                                )
                            )
                            break
                    else:
                        result.not_found.append(word)
                else:
                    result.not_found.append(word)

                break
            except requests.RequestException:
                if _ == max_attempts - 1:
                    result.not_found.append(word)

    return result


def clean_definition(text):
    # Remove HTML tags
    text = re.sub(r"<[^>]+>", "", text)
    # Remove special Wiktionary markup
    text = re.sub(r"\{\{[^}]+\}\}", "", text)
    # Remove square brackets and their contents
    text = re.sub(r"\[[^\]]+\]", "", text)
    # Remove parentheses and their contents
    text = re.sub(r"\([^)]+\)", "", text)
    # Remove extra whitespace
    text = " ".join(text.split())
    return text.strip()
