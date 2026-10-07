# Technical Architecture & Pipeline Description

This document outlines the architecture, model selection, and data flow of the AI Meeting Assistant developed for the Inter IIT Tech Meet 15.0. The application implements a sequential, three-stage multimodel pipeline to process meeting audio into highly accurate, structured documentation.

## System Architecture

The pipeline is built using a modular approach, separating audio transcription from linguistic refinement and structured data extraction. The user interface is handled via Streamlit, providing an interactive frontend for uploading audio, viewing intermediate outputs, and downloading final results.

### Stage 1: Audio Input and Transcription
* **Model Identified:** `faster-whisper` (Model size: `base.en`)
* **Role:** Transcribes the uploaded English-language audio recording into a raw text format.
* **Data Flow & Processing:** 
  * The user uploads an audio file (MP3/WAV/M4A) via the Streamlit interface.
  * The application loads the audio into the `faster-whisper` model, executing local CPU inference.
  * The model identifies spoken words, names, numbers, and negations, outputting a continuous string of text. 
  * **Output:** The foundational **Raw Transcript**.

### Stage 2: Domain-Aware Transcript Refinement
* **Model Identified:** `openai/gpt-oss-120b` (Accessed via Groq API)
* **Role:** Acts as a specialized transcript proofreader to correct plausible transcription errors in technical terms, acronyms, and domain-specific language.
* **Data Flow & Processing:** 
  * The Raw Transcript is passed to the Language Model along with a strict system prompt (`REFINEMENT_PROMPT`).
  * The LLM analyzes the text to fix domain terminology while explicitly preserving the speaker's original intent, commitments, and grammatical structure (e.g., maintaining negations). 
  * **Output:** The **Refined Transcript**.

### Stage 3: Meeting Minutes and Structured Extraction
* **Model Identified:** `openai/gpt-oss-120b` (Accessed via Groq API)
* **Role:** Analyzes the validated transcript to generate comprehensive meeting minutes, key decisions, and actionable tasks.
* **Data Flow & Processing:** 
  * The Refined Transcript is passed to this final LLM stage alongside the `DOCUMENTATION_PROMPT`.
  * The model is forced into JSON-mode to ensure the output strictly adheres to the required schema (`summary`, `minutes`, `decisions`, `action_items`).
  * **Constraint Handling:** The prompt enforces strict hallucination guardrails. If a task is assigned but the owner or deadline is not explicitly stated in the audio, the model is instructed to output `"Unspecified"` rather than guessing or fabricating details.
  * **Output:** A structured JSON object containing the finalized meeting documentation.

## Output Generation & Export
Once the pipeline concludes, the Streamlit backend parses the JSON and renders the data in a human-readable format. The user is provided with two export options:
1. **Structured JSON:** A machine-readable file containing the exact schema parsed by Stage 3.
2. **Text Report:** A complete, human-readable markdown summary combining the Raw Transcript, Refined Transcript, Minutes, Decisions, and Action Items into a single cohesive document.