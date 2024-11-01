# translate_srt.py

import logging
from typing import Any, Dict, List

import streamlit as st
from autogen import GroupChat, GroupChatManager

from agent_definitions import merge_agent_definitions
from agents import create_agents
from constants import (
    FORMATTED_SUBTITLES_END,
    FORMATTED_SUBTITLES_START,
    LANGUAGE_ENGLISH,
    LANGUAGE_FRENCH,
    LANGUAGE_GERMAN,
    LANGUAGE_ITALIAN,
    LANGUAGE_SPANISH,
    LANGUAGE_TURKISH,
    MAX_SUBTITLE_LINE_LENGTH,
    MAX_SUBTITLE_LINES,
    TERMINATION_MESSAGE,
)


def translate_srt_main(srt_content: str, source_lang: str, target_lang: str) -> str:
    # Create agents
    agents = create_agents(st.session_state.llm_config)

    # Set up the group chat
    group_chat = GroupChat(
        agents=[
            agents["user_proxy"],
            agents["subtitle_translator"],
            agents["translation_reviewer"],
            agents["subtitle_formatter"],
        ],
        messages=[],
        max_round=50,
    )

    # Create the manager
    manager = GroupChatManager(
        groupchat=group_chat, llm_config=st.session_state.llm_config
    )

    # Start the conversation
    logging.info("Starting conversation")
    user_proxy = agents["user_proxy"]

    task_description = f"""
    {merge_agent_definitions(source_lang, target_lang)}

    Input:
    Original SRT content in {source_lang}:
    {srt_content}
    User_Proxy, please start the conversation by calling Subtitle_Translator with the original SRT content.
    """
    chat_result = user_proxy.initiate_chat(
        manager,
        message=task_description,
    )

    # Extract the full translation from the chat result
    logging.info("Extracting translated content")
    translated_content = ""
    logging.info(f"Chat result: {chat_result}")

    # Extract translated content
    assistant_messages = [
        message["content"]
        for message in chat_result.chat_history
        if message.get("name") == "Subtitle_Formatter"
        and (
            FORMATTED_SUBTITLES_START in message.get("content", "")
            or FORMATTED_SUBTITLES_END in message.get("content", "")
        )
    ]
    if assistant_messages:
        translated_content = assistant_messages[-1].strip()
        # Remove any formatting markers
        translated_content = translated_content.replace(FORMATTED_SUBTITLES_START, "")
        translated_content = translated_content.replace(FORMATTED_SUBTITLES_END, "")
        translated_content = translated_content.replace(TERMINATION_MESSAGE, "")
        translated_content = translated_content.replace("```", "")
        translated_content = translated_content.strip()
    else:
        logging.warning("No properly formatted messages from Subtitle_Formatter")
        # Extract any content from Subtitle_Translator as a fallback
        translator_messages = [
            message["content"]
            for message in chat_result.chat_history
            if message.get("name") == "Subtitle_Translator" and message.get("content")
        ]
        if translator_messages:
            translated_content = translator_messages[-1].strip()
            logging.info("Using content from Subtitle_Translator as fallback")
        else:
            logging.error("No content found from any relevant agent")

    if not translated_content:
        logging.error("Translated content is empty")
        raise ValueError("Failed to obtain translated content")
    logging.info(
        f"Successfully extracted translated content: {translated_content[:100]}..."
    )
    return translated_content
