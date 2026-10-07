import os
from pathlib import Path
from pydub import AudioSegment

Path("INPUT").mkdir(exist_ok=True)
Path("PROCESSED").mkdir(exist_ok=True)
Path("CHUNKS_DIR").mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {".mp3", ".mp4", ".wav", ".mov", ".m4a"}

def validate_file(file_path: str) -> Path:
    p = Path(file_path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found at: {file_path}")
    if not p.is_file():
        raise ValueError(f"Path is not a regular file: {file_path}")
    if p.stat().st_size == 0:
        raise ValueError("Uploaded file is empty (0 bytes). Please upload a valid recording.")
    if p.suffix.lower() not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise ValueError(f"Unsupported format '{p.suffix}'. Supported formats are: {allowed}")
    return p

def convert_to_wav(file_path: str) -> str:
    base_name, _ = os.path.splitext(file_path)
    output_file = base_name + ".wav"
    try:
        audio = AudioSegment.from_file(file_path)
        audio.export(output_file, format="wav")
        return output_file
    except Exception as e:
        raise RuntimeError(
            f"Failed to convert '{file_path}' to WAV. "
            f"Please ensure FFmpeg is installed on your system. Error details: {e}"
        )

def chunking(output_file: str, chunk_time: int = 5, chunk_time_minutes: int = None) -> list:
    if chunk_time_minutes is not None:
        chunk_time = chunk_time_minutes
    if chunk_time <= 0:
        chunk_time = 5

    try:
        audio = AudioSegment.from_file(output_file)
    except Exception as e:
        raise RuntimeError(
            f"Could not load audio for splitting. Ensure FFmpeg is accessible. Error: {e}"
        )

    if len(audio) == 0:
        raise ValueError("Audio recording is silent or has zero duration.")

    chunk_ms = chunk_time * 60 * 1000
    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_file = f"PROCESSED/chunk_{i + 1}.wav"
        chunk.export(chunk_file, format="wav")
        chunks.append(chunk_file)

    return chunks











    




