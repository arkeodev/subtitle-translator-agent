# agents.py

import json
import logging
from typing import Any, Dict

from autogen.agentchat import AssistantAgent, UserProxyAgent

from constants import AGENT_CONFIG_FILE, UTF8_ENCODING, AgentType
from subtitle_utils import (
    format_subtitles,
    get_wiktionary_definition,
    parse_srt,
    verify_alignment,
)


def load_agent_configs() -> Dict[str, Any]:
    logging.info("Loading agent configurations")
    with open(AGENT_CONFIG_FILE, "r", encoding=UTF8_ENCODING) as f:
        return json.load(f)


def create_agents(llm_config: Dict[str, Any]) -> Dict[str, AgentType]:
    logging.info(f"Creating agents with llm_config: {llm_config}")

    agent_configs = load_agent_configs()
    agents: Dict[str, Any] = {}

    # Create a separate config for UserProxyAgent
    user_proxy_config = {"code_execution_config": {"use_docker": False}}

    subtitle_translator = AssistantAgent(
        name="Subtitle_Translator",
        system_message=agent_configs["subtitle_translator"]["system_message"],
        description=agent_configs["subtitle_translator"]["description"],
        llm_config=llm_config,
    )

    translation_reviewer = AssistantAgent(
        name="Translation_Reviewer",
        system_message=agent_configs["translation_reviewer"]["system_message"],
        description=agent_configs["translation_reviewer"]["description"],
        llm_config=llm_config,
    )

    subtitle_formatter = AssistantAgent(
        name="Subtitle_Formatter",
        system_message=agent_configs["subtitle_formatter"]["system_message"],
        description=agent_configs["subtitle_formatter"]["description"],
        llm_config=llm_config,
    )

    user_proxy = UserProxyAgent(
        name="User_Proxy",
        system_message=agent_configs["user_proxy"]["system_message"],
        description=agent_configs["user_proxy"]["description"],
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content", "")
        .rstrip()
        .endswith("TERMINATE"),
        code_execution_config=user_proxy_config["code_execution_config"],
    )
    # Register specific functions for each agent
    subtitle_translator.register_for_llm(
        description="Get definitions of words from wiktionary.com (limited attempts and words)"
    )(get_wiktionary_definition)
    subtitle_formatter.register_for_llm(
        description="Format subtitles according to specified rules"
    )(format_subtitles)
    subtitle_formatter.register_for_llm(
        description="Verify alignment between original and formatted subtitles"
    )(verify_alignment)

    # Register all functions for execution by UserProxyAgent
    user_proxy.register_for_execution()(get_wiktionary_definition)
    user_proxy.register_for_execution()(format_subtitles)
    user_proxy.register_for_execution()(verify_alignment)

    agents = {
        "subtitle_translator": subtitle_translator,
        "translation_reviewer": translation_reviewer,
        "subtitle_formatter": subtitle_formatter,
        "user_proxy": user_proxy,
    }

    return agents
