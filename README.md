# Subtitle Translator

Subtitle Translator is a Streamlit-based web application that translates SRT subtitle files from various languages to Turkish. It uses OpenAI's GPT-4 model for high-quality translations while maintaining the original SRT file format.

## Features

- Translate SRT files from English, French, German, Italian, or Spanish to Turkish
- Maintain original SRT formatting, including subtitle numbering and timestamps
- User-friendly web interface built with Streamlit
- Utilizes OpenAI's GPT-4 for accurate translations

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/subtitle-translator.git
   cd subtitle-translator
   ```

2. Create and activate a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up your OpenAI API key:
   Create a `.env` file in the project root and add your OpenAI API key:

   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

1. Run the Streamlit app:

   ```bash
   streamlit run app.py
   ```

2. Open your web browser and navigate to the provided local URL (usually `http://localhost:8501`).

3. Upload your SRT file and select the original language.

4. Click the "Translate" button to start the translation process.

5. Once completed, you can view the translated subtitles and download the new SRT file.

## Project Structure

- `app.py`: Main Streamlit application
- `translate_srt.py`: Core translation logic
- `agents.py`: Agent definitions for the translation process
- `utils.py`: Utility functions
- `agent_config.json`: Configuration for different agents used in the translation process

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgements

This project uses OpenAI's GPT-4 model for translations and Streamlit for the web interface.
