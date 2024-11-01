# app.py

import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st
from dotenv import load_dotenv

from constants import (
    DATA_DIR,
    HUGGINGFACE_MODEL_GEMMA,
    HUGGINGFACE_MODEL_META_LLAMA_70B,
    HUGGINGFACE_MODEL_META_LLAMA_405B,
    HUGGINGFACE_MODEL_MIXTRAL,
    LANGUAGE_ENGLISH,
    LANGUAGE_FRENCH,
    LANGUAGE_GERMAN,
    LANGUAGE_ITALIAN,
    LANGUAGE_SPANISH,
    LANGUAGE_TURKISH,
    MODEL_PROVIDER_HUGGINGFACE,
    MODEL_PROVIDER_OLLAMA,
    MODEL_PROVIDER_OPENAI,
    OLLAMA_API_KEY,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL_LLAMA31,
    OPENAI_MODEL_GPT4O,
    OPENAI_MODEL_GPT4O_MINI,
    OPENAI_MODEL_O1_MINI,
    OPENAI_MODEL_O1_PREVIEW,
    SRT_EXTENSION,
)
from translate import translate_srt_main
from utils import (
    calculate_subtitle_stats,
    ensure_byte_order_mark,
    load_css,
    load_subtitle_file,
    merge_subtitles,
    read_srt_file,
    remove_byte_order_mark,
    save_uploaded_file,
    set_api_keys,
    setup_logging,
    split_subtitles,
)


def initiate_translation_process(
    file_content: str, original_language: str, target_language: str
) -> str:
    logging.info("Initiating translation process")
    chunk_data = split_subtitles(file_content)
    translated_chunks = []
    for chunk in chunk_data:
        translated_chunk = translate_srt_main(
            chunk,
            original_language,
            target_language,
        )
        translated_chunks.append(translated_chunk)
    return merge_subtitles(translated_chunks)


def generate_llm_config(
    model_provider: str, model: str, temperature: float
) -> Dict[str, Any]:
    llm_config: Dict[str, Any] = {"temperature": temperature}
    if model_provider == MODEL_PROVIDER_OPENAI:
        llm_config["config_list"] = [{"model": model}]
    elif model_provider == MODEL_PROVIDER_OLLAMA:
        llm_config["config_list"] = [
            {
                "base_url": OLLAMA_BASE_URL,
                "api_key": OLLAMA_API_KEY,
                "model": model,
                "use_docker": False,
            }
        ]
    elif model_provider == MODEL_PROVIDER_HUGGINGFACE:
        api_key = os.getenv("HUGGINGFACEHUB_API_TOKEN")
        llm_config["config_list"] = [
            {
                "base_url": OLLAMA_BASE_URL,
                "api_key": api_key,
                "model": model,
                "use_docker": False,
            }
        ]
    return llm_config


def main():
    # Get port from command line argument or use default
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8501

    # Set port for Streamlit
    os.environ['STREAMLIT_SERVER_PORT'] = str(port)

    # Configure Streamlit to use the specified port
    st.set_page_config(
        page_title="Subtitle Translator",
        page_icon="🔄",
        layout="wide",
        menu_items={
            "Get Help": None,
            "Report a bug": None,
            "About": "Subtitle Translator v1.0",
        },
    )

    # Set up graceful shutdown handler
    def handle_shutdown():
        logging.info("Shutting down Subtitle Translator application...")
        sys.exit(0)

    # Register shutdown handler
    st.session_state.on_shutdown = handle_shutdown

    setup_logging()
    load_css()
    set_api_keys()
    logging.info("Starting Subtitle Translator application")

    st.title("Subtitle Translator")

    # Read OpenAI key from .env file
    openai_key = os.getenv("OPENAI_API_KEY")

    # Initialize session state variables
    if "file_content" not in st.session_state:
        st.session_state.file_content: Optional[str] = None
    if "translated_content" not in st.session_state:
        st.session_state.translated_content: Optional[str] = None
    input_file_path: Optional[str] = None
    output_file_path: Optional[str] = None
    issues: Optional[List[str]] = None

    # New radio button for selecting mode
    mode = st.radio(
        "Select Mode", ["Translate a subtitle file", "Edit a subtitle file"]
    )

    col1, col2, col3 = st.columns((1, 2, 2))

    with col1:
        st.subheader("Settings")

        if mode == "Translate a subtitle file":
            # Model provider selection
            model_provider = st.selectbox(
                "Select Model Provider",
                [
                    MODEL_PROVIDER_OPENAI,
                    MODEL_PROVIDER_OLLAMA,
                    MODEL_PROVIDER_HUGGINGFACE,
                ],
            )

            if model_provider == MODEL_PROVIDER_OPENAI:
                if not openai_key:
                    st.error(
                        "OpenAI API key not found. Please set it in the .env file."
                    )
                else:
                    st.success("OpenAI API key loaded successfully.")
                model = st.selectbox(
                    "Select OpenAI Model",
                    [
                        OPENAI_MODEL_GPT4O_MINI,
                        OPENAI_MODEL_GPT4O,
                        OPENAI_MODEL_O1_MINI,
                        OPENAI_MODEL_O1_PREVIEW,
                    ],
                )
            elif model_provider == MODEL_PROVIDER_OLLAMA:
                model = st.selectbox("Select Ollama Model", [OLLAMA_MODEL_LLAMA31])
            elif model_provider == MODEL_PROVIDER_HUGGINGFACE:
                model = st.selectbox(
                    "Select HuggingFace Model",
                    [
                        HUGGINGFACE_MODEL_META_LLAMA_70B,
                        HUGGINGFACE_MODEL_MIXTRAL,
                        HUGGINGFACE_MODEL_GEMMA,
                        HUGGINGFACE_MODEL_META_LLAMA_405B,
                    ],
                )
            temperature = st.slider(
                "Select Temperature",
                min_value=0.0,
                max_value=1.0,
                value=0.0,
                step=0.1,
            )

            # Generate and store llm_config in session state
            st.session_state.llm_config = generate_llm_config(
                model_provider, model, temperature
            )

            # Language selection
            st.session_state.original_language = st.selectbox(
                "Select Original Language",
                [
                    LANGUAGE_ENGLISH,
                    LANGUAGE_FRENCH,
                    LANGUAGE_GERMAN,
                    LANGUAGE_ITALIAN,
                    LANGUAGE_SPANISH,
                ],
            )
            st.session_state.target_language = st.selectbox(
                "Select Target Language", [LANGUAGE_TURKISH], disabled=True
            )

            uploaded_file = st.file_uploader(
                "Select a Subtitle File to Translate", type=SRT_EXTENSION
            )
            if uploaded_file is not None:
                input_file_path = save_uploaded_file(uploaded_file, suffix="-original")
                st.session_state.file_content = read_srt_file(input_file_path)

            if st.button("Translate"):
                if st.session_state.file_content is None:
                    st.error("Please upload a subtitle file to translate.")
                else:
                    # Perform translation using the new function
                    st.session_state.translated_content = initiate_translation_process(
                        st.session_state.file_content,
                        st.session_state.original_language,
                        st.session_state.target_language,
                    )

            if st.session_state.translated_content:
                if st.button("Save Translation"):
                    output_dir = Path(DATA_DIR)
                    output_dir.mkdir(exist_ok=True)
                    output_file_path = (
                        output_dir / f"{Path(input_file_path).stem}-tr{SRT_EXTENSION}"
                    )
                    with open(output_file_path, "w", encoding="utf-8") as f:
                        f.write(st.session_state.translated_content)
                    st.success(f"Translation saved to {output_file_path}")

    with col2:
        st.subheader("Original Subtitles")
        if st.session_state.file_content is not None:
            content_without_bom = remove_byte_order_mark(st.session_state.file_content)
            st.text_area(
                "Original Subtitles",
                content_without_bom,
                height=600,
                disabled=True,
                label_visibility="hidden",
                key="original_subtitles",
            )
        if mode == "Edit a subtitle file":
            original_file = st.file_uploader(
                "Load Original Subtitle File",
                accept_multiple_files=False,
                type=SRT_EXTENSION,
            )
            if original_file is not None:
                st.session_state.original_file_path = save_uploaded_file(
                    original_file, suffix="-original"
                )
                original_content = load_subtitle_file(
                    st.session_state.original_file_path
                )
                if original_content:
                    st.session_state.file_content = original_content
                    logging.info(
                        f"Files loaded: Original - {st.session_state.original_file_path}"
                    )
                    if st.button("Show File", key="show_edited_original_file"):
                        st.session_state.file_content = ensure_byte_order_mark(
                            original_content
                        )
                        st.experimental_rerun()
                else:
                    st.error("Failed to load subtitle files.")

    with col3:
        st.subheader("Translated/Edited Subtitles")
        if st.session_state.translated_content is not None:
            content_without_bom = remove_byte_order_mark(
                st.session_state.translated_content
            )
            edited_content = st.text_area(
                "Translated/Edited Subtitles",
                content_without_bom,
                height=600,
                label_visibility="hidden",
                key="translated_subtitles",
            )
            st.session_state.translated_content = edited_content

        if mode == "Edit a subtitle file":
            edited_file = st.file_uploader(
                "Load Translated/Edited Subtitle File",
                accept_multiple_files=False,
                type=SRT_EXTENSION,
            )
            if edited_file is not None:
                st.session_state.edited_file_path = save_uploaded_file(
                    edited_file, suffix="-edited"
                )
                edited_content = load_subtitle_file(st.session_state.edited_file_path)
                if edited_content:
                    st.session_state.translated_content = edited_content
                    logging.info(
                        f"Files loaded: Edited - {st.session_state.edited_file_path}"
                    )
                    if st.button("Show File", key="show_edited_translated_file"):
                        st.session_state.translated_content = ensure_byte_order_mark(
                            edited_content
                        )
                        st.experimental_rerun()
                else:
                    st.error("Failed to load subtitle files.")

    # Edit a subtitle file
    if mode == "Edit a subtitle file":
        if st.session_state.translated_content:
            if st.button("Save Edited File"):
                confirm_overwrite = st.warning(
                    "Are you sure you want to overwrite the original file?", icon="⚠️"
                )
                col_confirm1, col_confirm2 = confirm_overwrite.columns(2)
                with col_confirm1:
                    st.button("Overwrite", on_click=overwrite_file)
                with col_confirm2:
                    st.button("Cancel", on_click=cancel_overwrite)

    # Add a new section for subtitle statistics
    st.markdown("---")
    col_stats1, col_stats2 = st.columns((1, 4))
    with col_stats1:
        st.subheader("Statistics")
        if st.button("Calculate Statistics", use_container_width=True):
            if (
                st.session_state.file_content is not None
                and st.session_state.translated_content is not None
            ):
                issues = calculate_subtitle_stats(
                    st.session_state.file_content, st.session_state.translated_content
                )
            else:
                st.error(
                    "Both original and translated content must be available to calculate statistics."
                )
    with col_stats2:
        if issues:
            st.text_area("Subtitle Issues", "\n".join(issues), height=200)

    # Debug information
    st.markdown("---")
    st.subheader("Debug Information")
    st.write(f"File content available: {st.session_state.file_content is not None}")
    st.write(
        f"Translated content available: {st.session_state.translated_content is not None}"
    )
    if st.session_state.translated_content is not None:
        st.write(
            f"Translated content preview: {st.session_state.translated_content[:100]}..."
        )


def overwrite_file():
    save_path = st.session_state.original_file_path
    logging.info(f"Saving edited file to: {save_path}")
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(st.session_state.translated_content)
    st.success(f"File saved successfully to: {save_path}")


def cancel_overwrite():
    st.info("File save cancelled.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Received shutdown signal")
        sys.exit(0)
