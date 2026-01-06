---
title: sample-app
app_file: ui.py
sdk: gradio
sdk_version: 5.44.1
---



## Quick Setup

   1. Create virtual environment (Python 3.11)
      ```bash
      uv venv --python=python3.11 .venv


   2. Activate the virtual environment:
      ```bash
      source .venv/bin/activate
      ```

   3. Install dependencies:
      ```bash
      uv sync
      ```
      (This creates the virtual environment and installs all dependencies from `pyproject.toml` and `uv.lock`)

   4. Copy the example environment variables and update them:
      ```bash
      cp env.example .env
      ```
      Fill in `OPENAI_API_KEY` and adjust any other values as needed.

   5. Alternative setup (macOS / Linux):
      ```bash
      bash scripts/setup.sh
      ```
      Alternative setup (Windows - CMD or PowerShell):
      ```powershell
      setup.cmd
      ```
      (This runs `scripts/setup.ps1` with the necessary execution policy bypass.)

   6. Launch the Gradio UI:
      ```bash
      python ui.py
      ```



   Environment variables:

   - `OPENAI_API_KEY` (required) – OpenAI credentials used by the summarizer.
   - `OPENAI_MODEL`, `OPENAI_TEMPERATURE`, `WHISPER_MODEL` – optional model overrides.
   - `MAX_FILE_SIZE` – max upload size in MB (defaults to 50).
   - `PORT` – port for the Gradio server (defaults to 7860).
   - `GRADIO_SHARE` – set `true` to generate a share link when running locally.
   - `LOG_LEVEL`, `LOG_FILE` – optional logging configuration.


## Project Structure

- **`config/`**: Centralized application configuration.
  - **`settings.py`**: Environment-driven settings (API keys, ports, file size limits, etc.).
- **`models/`**: Pydantic data models and schemas.
  - **`meeting_schema.py`**: JSON schema for structured meeting summaries used by `summaryTool`.
- **`tools/`**: Core AI tools and processing pipelines.
  - **`speechToTextTool.py`**: Converts meeting audio to text using Whisper.
  - **`textRefiningTool.py`**: Cleans and refines raw transcripts before summarization.
  - **`summaryTool.py`**: Calls the LLM to generate a structured JSON summary of the meeting.
  - **`speakerEmbeddingTool.py`**: Handles speaker diarization, embedding extraction, and speaker identification.
- **`utils/`**: Helper utilities and shared infrastructure.
  - **`file_utils.py`**: File validation, conversion to 16k mono WAV, and simple I/O helpers.
  - **`hf_compat.py`**: Hugging Face compatibility shim for older libraries and token handling.
  - **`logging_config.py`**: Central logging configuration.
  - **`openai_client.py`**: Singleton OpenAI client wrapper.
  - **`model_factory.py`**: Lazy-loading factory for Hugging Face and Whisper models.
- **`sample-meetings/`**: Example meeting audio files you can use for local testing of the meeting summarizer.
- **`stored-speakers/`**: Enrollment data for known speakers.
  - **`speakers-data.json`**: Configuration describing each enrolled speaker and their enrollment audio files.
  - `*.wav` / `*.m4a`: Clean enrollment samples per speaker, used to build the speaker embedding store.
  - **`speaker_enrollment_samples.md`**: Documentation and notes about how speaker samples were recorded and used.
- **`scripts/`**: Utility scripts.
  - **`load-stored-speakers.py`**: Preprocesses and registers speakers from `stored-speakers/` into the embedding store.
- **`ui.py`**: Gradio-based web UI with two tabs:
  - **Meeting Summarizer**: Upload a meeting recording and get a structured, Markdown-formatted summary.
  - **Voice Recognition**: Upload a short voice clip to match against enrolled speakers.
- **`main.py`**: Orchestrates the end-to-end pipeline (`summaryAgent` and `voiceRecognitionAgent`).


## Tools & Workflows

### Meeting Summarizer (voice → transcript → summary)

- **UI Tab**: `Meeting Summarizer`
- **Input type**:
  - Single **audio file** of the full meeting.
  - Supported formats: **`.mp3`**, **`.wav`**, **`.m4a`**.
  - Recommended properties:
    - Clear speech from participants with minimal background noise.
    - Duration: from a few minutes up to the configured `MAX_FILE_SIZE` limit (default 50 MB).
- **What the tool does**:
  1. Converts audio to text using **Whisper**.
  2. Optionally refines/cleans the transcript.
  3. Generates a **structured JSON summary** using the `MeetingSummary` schema.
  4. Renders a **Markdown summary** with agenda, participants, topics, key points, action items, etc.
  5. Runs **speakerIdentificationTool** on the original audio to detect which enrolled speakers participated, and injects them into the “Detected Speakers” section at the top of the summary.
- **Best practices**:
  - Use mono or stereo recordings with distinct voices.
  - Avoid very low-volume or highly compressed audio.
  - For very short clips (< 5–10 seconds), use the **Voice Recognition** tab instead.


### Voice Recognition (who is speaking?)

- **UI Tab**: `Voice Recognition`
- **Input type**:
  - Single **short voice sample** from one speaker.
  - Supported formats: **`.mp3`**, **`.wav`**, **`.m4a`**.
  - Recommended duration: **≥ 2–3 seconds** of clear speech (longer gives better results).
- **What the tool does**:
  1. Converts the uploaded file to a **16kHz mono WAV** if needed.
  2. Uses **pyannote** diarization + embedding model to extract speaker embeddings.
  3. Compares the sample to the enrolled speakers stored in `speaker_store.pkl` (populated via `scripts/load-stored-speakers.py`).
  4. Returns:
     - `identified_speakers`: list of matching known speakers (e.g., `["Shubham", "Madhuri"]`).
     - `events`: step-by-step log messages shown in the UI (including confidence scores).
- **Audio requirements & tips**:
  - Use a **single speaker** per sample.
  - Avoid heavy background noise or music.
  - If the audio is **too short** or contains no clear speech, you will see a friendly error like:
    > “Audio file is too short… Please use a longer audio file for speaker identification.”
  - Make sure you have run `python scripts/load-stored-speakers.py` at least once to build the speaker store.


## Scripts

   ### `load-stored-speakers.py`

      This script is used to **load and register pre-defined speakers** into the system.  
      It reads speaker metadata from `speakers-data.json` and processes each speaker **one by one** to prepare them for speaker identification.

      #### What this script does
      - Reads the `speakers-data.json` file
      - Iterates through each speaker entry sequentially
      - Loads the associated audio file for each speaker
      - Registers / stores speaker information for later identification

      #### When to run this script
      - During initial project setup
      - When adding new known speakers
      - When rebuilding the speaker store from scratch

      #### How to run
      ```bash
      python scripts/load-stored-speakers.py


## Steps to create app from scratch


   Agentic AI setup

   1) install cursor AI IDE
   2) create directory in any folder for example : mkdir sample-agentic-app
   3) install uv : curl -Ls https://astral.sh/uv/install.sh | sh (close the terminal and open it again to active it)
   4) run uv sync to create .vnenv file: uv sync
   5) create project.tom file that will work as package.json using : uv init
   6) run this command to activate jupyter : source .venv/bin/activate  # macOS/Linux
   7) create notebook file: either using : jupyter notebook or manually create file using cursor IDE
   8) create agent.py file to actually put your code for production 
   9) to install and add package in toml file: uv add OpenAI
   10) create account on huggingface using url : https://huggingface.co and create token( click on avatar and list will be visible)
   11) go to  cursor ide terminal and run the command: gradio deploy (it will ask some questions like token, space etc )
   12) create requirments.txt and packages.txt for dependencies on hugging face otherwise at hugging face portal u will get module not found error: uv pip freeze > requirements.txt
   13) crete packages.txt for dependencies like ffmpeg manually    
   14) sometimes u get issue of dependency at hugging face due to some incompatible versions with other versions so u can try running these dependencies on local first otherwise it takes time if u directly do it on hugging face: python3 -m pip install -r requirements.txt

   Notes

   1) jupyter helps to give web interface to write run python code
   2) just to install the package we can run : uv pip install OpenAI 
   3) to install and add package in toml file: uv add OpenAI
   4) notebook we use just for testing and run the code locally but usually not in prod
   5) if you are facing dependency conflict/incompatible issue then run : python3 -m piptools compile requirements.in
   6) install packages locally : python3 -m venv .venv && source .venv/bin/activate && uv pip install -r requirements.txt

## Some important commands:

- Install dependencies on existing project: `uv sync`
- Install ffmpeg: `brew install ffmpeg`
- Activate Virtual Environment: `source .venv/bin/activate`
- Run project locally: `python3 ui.py`
- Install and add package in toml file: `uv add OpenAI`
- Log in to Hugging Face: `huggingface-cli login`
- Deploy to Hugging Face Spaces: `gradio deploy`
- convert m4a file to wav: 

   ffmpeg -y \
   -i stored-speakers/shubham-voice-to-identify.wav \
   -ac 1 \
   -ar 16000 \
   -acodec pcm_s16le \
   -af "silenceremove=1:0:-50dB,aresample=16000" \
   stored-speakers/shubham-voice-to-identify_16k.wav


## Ruff linting and formatting:

- Check for lint issues: `uv run ruff check .`
- Auto-fix lint issues: ` uv run ruff check --fix .`
- Check formatting: `uv run ruff format --check`
- Auto-format code: `uv run ruff format`
- Check lint for one file: `uv run ruff check path/to/file.py`
- Auto-fix lint for one file: `uv run ruff check --fix path/to/file.py`
- Check formatting for one file: `uv run ruff format --check path/to/file.py`
- Auto-format one file: `uv run ruff format path/to/file.py`

Lint vs. format:

- **Linting** finds code-quality and correctness issues, such as unused imports or unreachable branches.  
  *Example: `ruff check .` highlights an unused variable so you can remove it.*
- **Formatting** enforces consistent styling choices—spacing, quotes, line length—without changing behavior.  
  *Example: `ruff format` rewrites `x=1+2` to `x = 1 + 2` while keeping the same result.*



TODO

Add agent that get the transcripted text and try to improvise the textRefiningTool.py