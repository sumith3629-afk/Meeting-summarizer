# Technical Architecture & Pipeline Specification

## 1. Executive Overview

This application implements a multi-model meeting intelligence pipeline designed to ingest spoken English meeting recordings, transcribe them accurately, correct domain-specific technical terminology, and extract structured meeting minutes, agreed decisions, and actionable tasks.

A key design requirement of the problem statement is strict factual fidelity:
- Proposals or ongoing discussions must **not** be misrepresented as agreed decisions.
- Action items without a stated owner or deadline must explicitly mark them as `"unspecified"`, avoiding model hallucinations or assumptions.

---

## 2. Model Selection & Roles

The architecture decouples the workflow into three distinct stages using dedicated models:

```
[ Audio / Video File ]
          │
          ▼
┌──────────────────────────────────────────────┐
│ Stage 1: Speech-to-Text (STT)                │
│ Model: Faster-Whisper (OpenAI Whisper small) │
│ Role: Raw audio-to-text acoustic decoding    │
└──────────────────────────────────────────────┘
          │
          ▼ Raw Transcript (.txt)
┌──────────────────────────────────────────────┐
│ Stage 2: Domain-Aware Refinement             │
│ Model: Mistral-7B (open-mistral-7b)          │
│ Role: Technical term, acronym & jargon fix   │
└──────────────────────────────────────────────┘
          │
          ▼ Refined Transcript (.txt)
┌──────────────────────────────────────────────┐
│ Stage 3: Meeting Documentation & Extraction  │
│ Model: Mistral-7B (open-mistral-7b)          │
│ Role: Minutes, decisions, action items       │
└──────────────────────────────────────────────┘
          │
          ├──────────────────────────┐
          ▼                          ▼
[ meeting_record.json ]    [ meeting_record.md ]
 (Machine-Readable)         (Human-Readable)
```

### Stage 1: Speech-to-Text Engine
- **Model**: `faster-whisper` (CTranslate2-optimized implementation of OpenAI Whisper, default: `small`).
- **Role**: Ingests converted 16kHz mono WAV audio, splits it into configurable chunks (default: 5 minutes) using `pydub`, and transcribes spoken speech into raw text.
- **Why this model**: `faster-whisper` runs up to 4x faster than standard PyTorch Whisper while consuming significantly less memory on CPU and GPU, making it responsive for local and cloud environments.

### Stage 2: Domain-Aware Transcript Refiner
- **Model**: Mistral-7B (`open-mistral-7b`) via LangChain.
- **Role**: Examines the raw acoustic transcription to fix phonetic misrecognitions of technical terms (e.g., framework names, database engines, cloud services, and engineering acronyms like `gRPC`, `P99`, `OAuth2`, `Kubernetes`).
- **Prompt Strategy**: Operates under strict preservation constraints:
  - Preserves exact numbers, names, negations, and commitments.
  - Retains natural spoken conversational structure without turning it into prose.
  - Prohibits inserting new facts or extrapolating.
- **Output**: Cleaned, domain-accurate transcript saved as `refined_transcript.txt`.

### Stage 3: Meeting Documentation & Task Extractor
- **Model**: Mistral-7B (`open-mistral-7b`) via LangChain.
- **Role**: Analyzes the refined transcript to extract structured intelligence:
  1. **Executive Summary**: High-level overview of the session.
  2. **Organized Minutes**: Topical breakdown of discussion points.
  3. **Key Decisions**: Concrete agreements only. If an item was merely suggested or debated without agreement, it is omitted. If no decision was reached, returns `[]`.
  4. **Actionable Tasks**: Specific work items. Each item includes a description, owner, and deadline. If an owner or deadline was not explicitly stated in the conversation, the model writes `"unspecified"`.
- **Parsing & Reliability**: Built-in JSON parser with `json_repair` fallback to guarantee schema compliance even if the model outputs minor JSON formatting flaws.

---

## 3. Data Flow Between Stages

1. **Upload & Preprocessing**:
   - The user uploads an audio/video file (`.mp3`, `.mp4`, `.wav`, `.mov`, `.m4a`).
   - The system checks file presence, type, and size (rejecting empty or corrupt files).
   - Audio is normalized to WAV format and divided into sequential chunks.

2. **Acoustic Transcription**:
   - Chunks are sequentially processed by Faster-Whisper.
   - Text segments are joined to produce the initial raw transcript.

3. **Refinement Pipeline**:
   - The raw transcript is passed into LLM 1 with the refinement prompt.
   - The resulting refined transcript is stored for side-by-side comparison.

4. **Structured Documentation Generation**:
   - The refined transcript is fed into LLM 2 with the structured schema prompt.
   - LLM 2 returns a validated JSON object conforming to the specification.
   - The system serializes the result into:
     - `meeting_record.json` (Machine-readable)
     - `meeting_record.md` (Human-readable formatted report with Markdown tables)

---

## 4. Anti-Hallucination & Fidelity Safeguards

- **Decisions vs. Proposals**: The prompt explicitly instructs LLM 2 to distinguish between proposals ("we could try gRPC") and consensus ("we agreed to keep Postgres").
- **Unspecified Fields**: Defaulting to `"unspecified"` prevents the common LLM trap of guessing deadlines (e.g., assuming "next week" or "end of sprint") or guessing owners based on who spoke last.
- **Zero-Shot Determinism**: Generation uses `temperature=0.0` for structured extraction to maintain reproducibility and factual consistency.
