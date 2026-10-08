# AI-Powered Meeting Assistant 🎙️

An end-to-end meeting intelligence pipeline that turns recorded meetings into accurate transcripts, domain-refined text, and structured documentation (executive summaries, organized minutes, agreed decisions, and actionable tasks).

Built for **Inter IIT Bootcamp Phase 2 (ML PS)**.

---

## 📌 Features

- **Robust Audio Ingestion**: Supports `.mp3`, `.mp4`, `.wav`, `.mov`, and `.m4a` files with validation and automatic audio track extraction.
- **Fast Acoustic Transcription**: Uses `faster-whisper` for fast, accurate speech-to-text processing.
- **Domain-Aware Refinement (LLM 1)**: Corrects technical jargon, acronyms, and phonetic misrecognitions while strictly preserving names, numbers, negations, and speaker intent.
- **Factual Minutes & Task Extraction (LLM 2)**: Extracts structured meeting minutes and action items with anti-hallucination guardrails:
  - Distinguishes confirmed decisions from mere proposals.
  - Leaves task owners and deadlines as `unspecified` if not explicitly mentioned in the recording.
- **Interactive UI**: Clean Streamlit dashboard with side-by-side transcript comparison and one-click downloads.
- **Dual Output Formats**: Generates both machine-readable (`.json`) and human-readable (`.md`) artifacts.

---

## 🏗️ Architecture & Pipeline

```
Meeting Audio/Video
        │
        ▼
[Audio Processing & Chunking] (pydub + ffmpeg)
        │
        ▼
[Stage 1: Speech-to-Text] ───► raw_transcript.txt
(Faster-Whisper small)
        │
        ▼
[Stage 2: Domain Refiner] ───► refined_transcript.txt
(Mistral-7B / LLM 1)
        │
        ▼
[Stage 3: Minutes & Tasks] ──► meeting_record.json & meeting_record.md
(Mistral-7B / LLM 2)
```

For full architectural details, model parameters, and prompt designs, refer to [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md).

---

## ⚙️ Prerequisites

1. **Python**: 3.10 or higher.
2. **FFmpeg**: Required by `pydub` to handle audio conversions and video extractions.
   - **Windows**: Install via `winget install Gyan.FFmpeg` or download from [gyan.dev](https://www.gyan.dev/ffmpeg/builds/) and add its `bin/` folder to your system `PATH`.
   - **Ubuntu/Debian**: `sudo apt update && sudo apt install ffmpeg`
   - **macOS**: `brew install ffmpeg`
3. **Mistral API Key**: Sign up at [console.mistral.ai](https://console.mistral.ai/) to get an API key.

---

## 🚀 Quickstart & Setup

### 1. Clone the repository
```bash
git clone https://github.com/sumith3629-afk/Meeting-summarizer.git
cd Meeting-summarizer
```

### 2. Set up a virtual environment
```bash
python -m venv .venv

# On Windows:
.venv\Scripts\activate

# On Linux/macOS:
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Create a `.env` file by copying the example:
```bash
cp .env.example .env
```
Open `.env` and paste your Mistral API key:
```env
MISTRAL_API_KEY=your_actual_mistral_api_key_here
MISTRAL_MODEL=open-mistral-7b
WHISPER_MODEL=small
```

*(Note: You can also enter your Mistral API Key directly in the Streamlit web sidebar if you prefer not to touch `.env`.)*

---

## 🖥️ Running the Application

### Option A: Interactive Web UI (Recommended)
Launch the Streamlit app:
```bash
streamlit run app.py
```
1. Open your browser at `http://localhost:8501`.
2. Upload your meeting recording (`.mp3`, `.wav`, `.mp4`, etc.).
3. (Optional) Provide your Mistral API key in the sidebar if not set in `.env`.
4. Click **🚀 Process Recording**.
5. Inspect the generated summary, side-by-side transcripts, minutes, decisions, and tasks.
6. Use the **Download Outputs** tab to save `.txt`, `.json`, and `.md` files.

### Option B: Command-Line Pipeline (CLI)
You can also run the full pipeline headless:
```bash
python main.py --file sample_data/sample_meeting.wav --chunk_minutes 5
```
Outputs will be saved in the project root:
- `raw_transcript.txt`
- `refined_transcript.txt`
- `meeting_record.json`
- `meeting_record.md`

---

## 📁 Repository Structure
├── app.py                     # Interactive Streamlit application
├── main.py                    # CLI runner for headless processing
├── summarize.py               # LLM stages: Refinement & Meeting Documentation
├── requirements.txt           # Python package dependencies
├── .env.example               # Template for environment configuration
├── TECHNICAL_REPORT.md        # Detailed model descriptions & stage flow
├── README.md                  # Setup and execution guide
├── Core/
│   └── transcriber.py         # Faster-Whisper transcription logic
├── utils/
│   └── audio_processor.py     # File validation, WAV conversion, and chunking
└── sample_data/               # Pre-packaged sample meeting recording & outputs
    ├── sample_meeting.wav     # 2-minute technical engineering sync recording
    ├── raw_transcript.txt     # Raw STT output
    ├── refined_transcript.txt # Domain-refined output
    ├── meeting_record.json    # Machine-readable structured record
    └── meeting_record.md      # Human-readable markdown record

## 📊 Sample Meeting Recording & Verifiable Outputs

We provide a bundled technical meeting recording in `sample_data/sample_meeting.wav`. It simulates an engineering standup discussing PostgreSQL vs MongoDB, Redis caching, gRPC proposals, Prometheus alerts, and Kubernetes.

You can inspect the pre-generated outputs inside `sample_data/`:
- **`raw_transcript.txt`**: Raw acoustic output from Faster-Whisper.
- **`refined_transcript.txt`**: Output after LLM 1 corrects technical terms and acronyms.
- **`meeting_record.json`**: Structured JSON validating that:
  - Agreed decisions (e.g., sticking with PostgreSQL, approving Redis) are captured.
  - Deferred proposals (e.g., gRPC) are not falsely marked as decisions.
  - Tasks without explicit owners or dates show `"unspecified"`.
- **`meeting_record.md`**: Formatted executive report with Markdown tables.

