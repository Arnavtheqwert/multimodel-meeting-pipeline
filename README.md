# AI-Powered Meeting Assistant | Inter IIT Tech Meet 15.0

## Project Overview
This repository contains an AI-powered meeting assistant designed to convert recorded meeting speech into an accurate transcript and structured documentation. The system uses a coordinated multimodel pipeline to transcribe audio, refine domain-specific terminology, and generate meeting minutes, key decisions, and actionable tasks. 

## Identified Models
As required by the submission guidelines, this pipeline utilizes the following models:
1. **Speech-to-Text Model:** `faster-whisper` (`base.en`) for fast, local audio transcription.
2. **Language Model (Transcript Refinement):** `openai/gpt-oss-120b` (via Groq API) tasked with correcting domain-specific terminology errors while preserving the original meaning.
3. **Language Model (Meeting Documentation):** `openai/gpt-oss-120b` (via Groq API) tasked with generating structured minutes, decisions, and action items, strictly omitting guessed owners or deadlines.

## Setup & Installation

**1. Prerequisites**
* Python 3.9 or higher.
* A valid Groq API key for language model processing.

**2. Install Dependencies**
Clone this repository and install the required packages:
```bash
git clone <your-repo-url>
cd <your-repo-name>
pip install -r requirements.txt
