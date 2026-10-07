import streamlit as st
import json
import os
from faster_whisper import WhisperModel
from openai import OpenAI # Used generically for any OpenAI-compatible API (Groq, local vLLM, etc.)
from prompts import REFINEMENT_PROMPT, DOCUMENTATION_PROMPT

# Configuration & Client Setup
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
client = OpenAI(
    api_key=os.environ.get("LLM_API_KEY", "your_api_key_here"),
    base_url="https://api.groq.com/openai/v1"
)
LLM_MODEL = "openai/gpt-oss-120b"
@st.cache_resource
def load_stt_model():
    return WhisperModel("./faster-whisper-base-en", device="cpu", compute_type="int8")

def transcribe_audio(audio_path, model):
    segments, info = model.transcribe(audio_path, beam_size=5)
    return " ".join([segment.text for segment in segments])

def call_llm(system_prompt, user_content, json_mode=False):
    kwargs = {"response_format": {"type": "json_object"}} if json_mode else {}
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content}
        ],
        temperature=0.1,
        **kwargs
    )
    return response.choices[0].message.content

st.set_page_config(page_title="AI Meeting Assistant", layout="wide")
st.title("🎙️ Automated Meeting Assistant Pipeline")

uploaded_file = st.file_uploader("Upload Meeting Audio (MP3/WAV)", type=["mp3", "wav", "m4a"])

if uploaded_file is not None:
    # Error Handling for empty/invalid files
    if uploaded_file.size == 0:
        st.error("Error: The uploaded file is empty. Please upload a valid audio recording.")
        st.stop()
        
    audio_path = f"temp_{uploaded_file.name}"
    with open(audio_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.button("Start Processing Pipeline"):
        with st.status("Running Multimodel Pipeline...", expanded=True) as status:
            st.write("⏳ Loading Speech-to-Text Model...")
            stt_model = load_stt_model()
            
            st.write("🎙️ Stage 1: Transcribing Audio...")
            raw_transcript = transcribe_audio(audio_path, stt_model)
            
            st.write("📝 Stage 2: Refining Domain Terminology...")
            refined_transcript = call_llm(REFINEMENT_PROMPT, raw_transcript)
            
            st.write("📋 Stage 3: Extracting Minutes & Action Items...")
            structured_data_str = call_llm(DOCUMENTATION_PROMPT, refined_transcript, json_mode=True)
            structured_data = json.loads(structured_data_str)
            
            status.update(label="Processing Complete!", state="complete", expanded=False)

        # Interactive Interface & Comparison
        st.header("1. Transcripts")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Raw Transcript")
            st.info(raw_transcript)
        with col2:
            st.subheader("Refined Transcript")
            st.success(refined_transcript)

        # Structured Output Presentation
        st.header("2. Meeting Documentation")
        st.subheader("Summary")
        st.write(structured_data.get("summary", "No summary available."))
        
        st.subheader("Minutes")
        for point in structured_data.get("minutes", []):
            st.markdown(f"- {point}")
            
        st.subheader("Key Decisions")
        decisions = structured_data.get("decisions", [])
        if not decisions:
            st.write("No decisions were reached.")
        else:
            for decision in decisions:
                st.markdown(f"- {decision}")
                
        st.subheader("Action Items")
        tasks = structured_data.get("action_items", [])
        if not tasks:
            st.write("No tasks were assigned.")
        else:
            for task in tasks:
                owner = task.get('owner', 'Unspecified')
                deadline = task.get('deadline', 'Unspecified')
                st.markdown(f"- **{task['description']}** (Owner: *{owner}*, Deadline: *{deadline}*)")

        # Downloadable Results
        st.header("3. Export Results")
        human_readable = f"""# Meeting Record\n\n## Summary\n{structured_data.get('summary')}\n\n## Refined Transcript\n{refined_transcript}"""
        
        col3, col4 = st.columns(2)
        col3.download_button("Download Text Report", human_readable, file_name="meeting_record.txt", type="primary")
        col4.download_button("Download Structured JSON", json.dumps(structured_data, indent=4), file_name="meeting_record.json")
        
        os.remove(audio_path)
