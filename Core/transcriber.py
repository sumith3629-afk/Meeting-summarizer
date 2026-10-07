import os 
from faster_whisper import WhisperModel
from dotenv import load_dotenv 
from pathlib import Path
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
load_dotenv()
MISTRAL_KEY = os.getenv("MISTRAL_API_KEY")
MODEL_SIZE = os.getenv("WHISPER_MODEL" , 'small')
model = None 
def load_model():
    global model
    if model is None:
        print("------------Model is loading------------")
        model = WhisperModel(MODEL_SIZE , device="cpu")
    return model 
def transcribe(chunk_path:str): 
    model = load_model()
    segments , info = model.transcribe(chunk_path)
    return " ".join(seg.text.strip() for seg in segments).strip()
def transcribe_all(chunks:list ):
    full_transcript = []
    for i , chunk in enumerate(chunks):
        print(f"Transcribing {i+1}/{len(chunks)}")
        text = transcribe(chunk)
        full_transcript.append(text) 
    return " ".join(full_transcript) 
def raw_transcript(full_transcript:str):
    with open("raw_transcript.txt" , "w") as f:
        f.write(full_transcript)
    return "raw_transcript.txt"



        