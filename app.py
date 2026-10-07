import os
import json
from pathlib import Path
import streamlit as st
import pandas as pd
from utils.audio_processor import validate_file, convert_to_wav, chunking
from Core.transcriber import transcribe_all
from summarize import refine_transcript, generate_meeting_record, format_as_markdown

st.set_page_config(
    page_title="AI Meeting Assistant",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

if "processed" not in st.session_state:
    st.session_state.processed = False
    st.session_state.raw_transcript = ""
    st.session_state.refined_transcript = ""
    st.session_state.meeting_record = {}
    st.session_state.markdown_report = ""

with st.sidebar:
    st.header("⚙️ Configuration")
    env_api_key = os.getenv("MISTRAL_API_KEY", "")
    api_key_input = st.text_input(
        "Mistral API Key",
        value=env_api_key,
        type="password",
        help="Reads from .env by default. Enter here if testing without a .env file."
    )
    chunk_minutes = st.slider("Chunk Size (Minutes)", min_value=1, max_value=10, value=5, help="Length of audio chunks for Whisper transcription")
    
    st.markdown("---")
    st.subheader("Pipeline Overview")
    st.markdown("""
    1. **STT Model**: Faster-Whisper (Speech-to-Text)
    2. **LLM 1**: Mistral-7B (Domain Refinement)
    3. **LLM 2**: Mistral-7B (Minutes & Task Extraction)
    """)
    st.info("Outputs reflect explicit statements only — unassigned tasks and unspecified deadlines remain 'unspecified'.")



st.markdown('<div class="main-header">🎙️ AI Meeting Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Automated Transcription, Domain Terminology Refinement & Structured Minutes</div>', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Upload meeting recording (Audio or Video)",
    type=["mp3", "mp4", "wav", "mov", "m4a"],
    help="Supported formats: MP3, MP4, WAV, MOV, M4A"
)

if uploaded_file:
    st.audio(uploaded_file)
    
    col_btn, _ = st.columns([1, 4])
    with col_btn:
        start_processing = st.button("🚀 Process Recording", type="primary", use_container_width=True)

    if start_processing:
        upload_dir = Path("INPUT")
        upload_dir.mkdir(exist_ok=True)
        saved_file_path = upload_dir / uploaded_file.name
        with open(saved_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        with st.status("Processing meeting recording...", expanded=True) as status:
            try:
                status.write(" Validating file format and size...")
                valid_path = validate_file(str(saved_file_path))
                status.write(" Converting audio track to WAV format...")
                if valid_path.suffix.lower() != ".wav":
                    wav_path = convert_to_wav(str(valid_path))
                else:
                    wav_path = str(valid_path)
                status.write(f" Splitting audio into {chunk_minutes}-minute chunks...")
                chunks = chunking(wav_path, chunk_minutes)
                status.write(f"Created {len(chunks)} chunk(s).")
                status.write(" Transcribing speech with Faster-Whisper...")
                raw_text = transcribe_all(chunks)
                st.session_state.raw_transcript = raw_text
                status.write(" Refining technical terminology with LLM 1 (Mistral)...")
                refined_text = refine_transcript(raw_text, api_key=api_key_input)
                st.session_state.refined_transcript = refined_text
                status.write(" Extracting summary, minutes, decisions, and action items with LLM 2...")
                record = generate_meeting_record(refined_text, api_key=api_key_input)
                st.session_state.meeting_record = record
                st.session_state.markdown_report = format_as_markdown(record)
                st.session_state.processed = True
                status.update(label="Processing complete!", state="complete", expanded=False)
                st.success("Meeting analysis completed successfully!")
            except Exception as e:
                status.update(label="Processing failed", state="error", expanded=True)
                st.error(f"Error during processing: {str(e)}")
if st.session_state.processed:
    st.markdown("---")
    st.subheader("Meeting Intelligence Dashboard")

    tab_summary, tab_compare, tab_minutes, tab_tasks, tab_downloads = st.tabs([
        " Executive Summary",
        " Transcript Comparison (Raw vs Refined)",
        " Minutes & Decisions",
        " Action Items",
        " Download Outputs"
    ])
    with tab_summary:
        st.markdown("### Executive Summary")
        summary_text = st.session_state.meeting_record.get("summary", "No summary available.")
        st.info(summary_text)
    with tab_compare:
        st.markdown("### Side-by-Side Transcript Comparison")
        st.caption("Compare the raw speech-to-text transcript against the domain-refined transcript.")
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Raw Transcript (Faster-Whisper)**")
            st.text_area("Raw", value=st.session_state.raw_transcript, height=450, label_visibility="collapsed")
        with col2:
            st.markdown("**Refined Transcript (Domain-Aware LLM 1)**")
            st.text_area("Refined", value=st.session_state.refined_transcript, height=450, label_visibility="collapsed")
    with tab_minutes:
        col_min, col_dec = st.columns([3, 2])
        
        with col_min:
            st.markdown("### Organized Meeting Minutes")
            minutes = st.session_state.meeting_record.get("meeting_minutes", [])
            if minutes:
                for idx, m in enumerate(minutes, 1):
                    with st.expander(f" {idx}. {m.get('topic', 'Topic')}", expanded=True):
                        st.write(m.get("discussion", ""))
            else:
                st.write("No minutes generated.")
        with col_dec:
            st.markdown("### Key Decisions")
            decisions = st.session_state.meeting_record.get("key_decisions", [])
            if decisions:
                for d in decisions:
                    st.success(f" **Decision:** {d}")
            else:
                st.warning("No explicit decisions agreed upon in this meeting.")
    with tab_tasks:
        st.markdown("### Actionable Tasks")
        tasks = st.session_state.meeting_record.get("action_items", [])
        if tasks:
            df_tasks = pd.DataFrame(tasks)
            for col in ["task", "owner", "deadline"]:
                if col not in df_tasks.columns:
                    df_tasks[col] = "unspecified"
            
            df_tasks.columns = [c.capitalize() for c in df_tasks.columns]
            st.dataframe(df_tasks, use_container_width=True, hide_index=True)
        else:
            st.info("No action items assigned in this meeting.")
    with tab_downloads:
        st.markdown("### Download Generated Outputs")
        st.write("Download both human-readable and machine-readable structured artifacts:")
        d_col1, d_col2 = st.columns(2)
        with d_col1:
            st.download_button(
                label="Download Raw Transcript (.txt)",
                data=st.session_state.raw_transcript,
                file_name="raw_transcript.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.download_button(
                label="Download Refined Transcript (.txt)",
                data=st.session_state.refined_transcript,
                file_name="refined_transcript.txt",
                mime="text/plain",
                use_container_width=True
            )
            
        with d_col2:
            st.download_button(
                label="Download Meeting Record (.md)",
                data=st.session_state.markdown_report,
                file_name="meeting_record.md",
                mime="text/markdown",
                use_container_width=True
            )
            st.download_button(
                label="Download Machine-Readable Record (.json)",
                data=json.dumps(st.session_state.meeting_record, indent=2),
                file_name="meeting_record.json",
                mime="application/json",
                use_container_width=True
            )
