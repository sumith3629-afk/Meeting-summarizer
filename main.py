import sys
import json
import argparse
from pathlib import Path
from utils.audio_processor import validate_file, convert_to_wav, chunking
from Core.transcriber import transcribe_all , raw_transcript
from summarize import refine_transcript, generate_meeting_record, format_as_markdown


def run(file_path:str , chunk_minutes:  int = 5):
    try:
        valid_path = validate_file(file_path)
        print("Validated file")
        if valid_path.suffix.lower() != ".wav":
            print("Converting to wav....")
            wav_path = convert_to_wav(valid_path)
        else:
            wav_path = valid_path
        print("Chunks are being created....")
        chunks = chunking(wav_path , chunk_minutes)
        print(f"Created {len(chunks)} chunks")
        print("Processing chunks....")
        raw_transcription = transcribe_all(chunks)
        raw_path = raw_transcript(raw_transcription)
        print(f"Raw transcript saved -> {raw_path}")
        print("Refining Transcript....")
        refined = refine_transcript(raw_transcription)
        with open("refined_transcript.txt", "w", encoding="utf-8") as f:
            f.write(refined)
        print("Refinement done -> saved refined_transcript.txt")

        print("Generating Minutes & Tasks....")
        record = generate_meeting_record(refined)
        with open("meeting_record.json", "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)
        print("Generation done -> saved meeting_record.json")

        print("Formatting as markdown....")
        final_md = format_as_markdown(record)
        with open("meeting_record.md", "w", encoding="utf-8") as f:
            f.write(final_md)
        with open("Meeting_summary.md", "w", encoding="utf-8") as f:
            f.write(final_md)
        print("Formatting done -> saved meeting_record.md and Meeting_summary.md")
        print("\nAll pipeline stages completed successfully!")
    except Exception as e:
        print(f"An Error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Meeting Assistant Pipeline")
    parser.add_argument("--file", "-f", type=str, help="Path to meeting audio/video file")
    parser.add_argument("--chunk_minutes", "-c", type=int, default=5, help="Chunk length in minutes")
    args = parser.parse_args()

    input_file = args.file if args.file else input("Enter path to meeting audio/video file: ").strip()
    if not input_file:
        print("Error: No file provided.", file=sys.stderr)
        sys.exit(1)

    run(input_file, args.chunk_minutes)
