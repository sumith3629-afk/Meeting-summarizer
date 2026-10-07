import os
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

MODEL_NAME = os.getenv("MISTRAL_MODEL", "open-mistral-7b")

def get_llm(temperature: float = 0.0, api_key: str = None) -> ChatMistralAI:
    key = api_key or os.getenv("MISTRAL_API_KEY")
    if not key:
        raise ValueError(
            "Mistral API key not found. Please provide it in the UI sidebar or set MISTRAL_API_KEY in your .env file."
        )
    return ChatMistralAI(
        model=MODEL_NAME,  
        api_key=key,
        temperature=temperature
    )

# ---------------------------------------------------------------------------
# STAGE 1: Domain-Aware Transcript Refinement
# ---------------------------------------------------------------------------
REFINEMENT_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert domain-aware transcript editor.
Your job is to refine raw speech-to-text transcripts by correcting speech recognition errors, phonetically misrecognized domain-specific words, acronyms, and technical jargon.

CRITICAL RULES:
1. Preserve the speaker's original meaning, intent, numbers, dates, speaker names, negations, and commitments.
2. Do NOT add new information, extrapolate, or invent details not in the raw transcript.
3. Do NOT rewrite the conversation into formal essay prose; keep the natural dialogue structure.
4. Return ONLY the refined transcript text with no extra conversational commentary or conversational preamble.
"""),
    ("user", "Here is the raw meeting transcript:\n\n{raw_transcript}")
])

def refine_transcript(raw_transcript: str, api_key: str = None) -> str:
    """Passes the raw transcript through LLM 1 for technical term and acronym correction."""
    if not raw_transcript or not raw_transcript.strip():
        raise ValueError("Raw transcript is empty.")
    
    llm = get_llm(temperature=0.1, api_key=api_key)
    chain = REFINEMENT_PROMPT | llm | StrOutputParser()
    refined = chain.invoke({"raw_transcript": raw_transcript})
    return refined.strip()
DOCUMENTATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an executive meeting secretary.
Your task is to analyze the refined meeting transcript and produce structured minutes, key decisions, and actionable tasks.

CRITICAL RULES:
1. SUMMARY: A concise executive summary of the meeting.
2. MEETING MINUTES: Organized topical breakdown of main discussion points.
3. KEY DECISIONS: A list of concrete decisions that were explicitly agreed upon. 
   - If no explicit decision was reached, return an empty list: [].
   - Do NOT present proposals, suggestions, or ongoing debates as agreed decisions.
4. ACTION ITEMS: A list of actionable tasks. Each action item must strictly have:
   - "task": The specific work to be done.
   - "owner": The assigned person's name. If no owner was explicitly assigned, you MUST write "unspecified". NEVER guess or assume an owner.
   - "deadline": The stated deadline or timeframe. If no deadline was stated, you MUST write "unspecified". NEVER invent dates.
   - If no action items were assigned, return an empty list: [].

OUTPUT FORMAT:
You MUST respond strictly with a valid JSON object. Do not include markdown code fence formatting (```json) or introductory chit-chat.
The JSON must follow this exact schema:
{{
  "summary": "Concise high-level summary of the meeting",
  "meeting_minutes": [
    {{
      "topic": "Topic title",
      "discussion": "Summary of discussion points for this topic"
    }}
  ],
  "key_decisions": [
    "Decision 1"
  ],
  "action_items": [
    {{
      "task": "Task description",
      "owner": "Person name or 'unspecified'",
      "deadline": "Due date or 'unspecified'"
    }}
  ]
}}
"""),
    ("user", "Here is the refined meeting transcript:\n\n{refined_transcript}\n\nStructured JSON:")
])

def _clean_json_output(raw_output: str) -> dict:
    """Strips markdown fences and parses JSON, repairing any minor syntax defects from the LLM."""
    cleaned = raw_output.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # 1. Try standard JSON parsing
    try:
        return json.loads(cleaned)
    except Exception:
        pass

    # 2. Try json_repair (fixes missing commas, unescaped quotes, trailing commas)
    try:
        import json_repair
        parsed = json_repair.loads(cleaned)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        pass

    # 3. Fallback regex extraction of outermost JSON object
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            import json_repair
            parsed = json_repair.loads(match.group(0))
            if isinstance(parsed, dict):
                return parsed
        except Exception:
            return json.loads(match.group(0))

    raise ValueError(f"Failed to parse LLM output as JSON: {raw_output}")


def generate_meeting_record(refined_transcript: str, api_key: str = None) -> dict:
    if not refined_transcript or not refined_transcript.strip():
        raise ValueError("Refined transcript is empty.")
    llm = get_llm(temperature=0.0, api_key=api_key)
    chain = DOCUMENTATION_PROMPT | llm | StrOutputParser()
    raw_response = chain.invoke({"refined_transcript": refined_transcript})
    return _clean_json_output(raw_response)
def format_as_markdown(record: dict) -> str:
    md = []
    md.append("# Meeting Minutes & Executive Record\n")
    md.append("## 1. Executive Summary")
    md.append(f"{record.get('summary', 'No summary provided.')}\n")
    
    md.append("## 2. Organized Meeting Minutes")
    minutes = record.get("meeting_minutes", [])
    if minutes:
        for idx, item in enumerate(minutes, 1):
            md.append(f"### 2.{idx} {item.get('topic', 'Discussion')}")
            md.append(f"{item.get('discussion', '')}\n")
    else:
        md.append("No discussion topics recorded.\n")
        
    md.append("## 3. Key Decisions")
    decisions = record.get("key_decisions", [])
    if decisions:
        for d in decisions:
            md.append(f"- {d}")
        md.append("")
    else:
        md.append("_No formal decisions were agreed upon during this meeting._\n")
        
    md.append("## 4. Action Items")
    tasks = record.get("action_items", [])
    if tasks:
        md.append("| # | Task | Owner | Deadline |")
        md.append("|---|---|---|---|")
        for idx, t in enumerate(tasks, 1):
            task_desc = t.get("task", "unspecified")
            owner = t.get("owner", "unspecified")
            deadline = t.get("deadline", "unspecified")
            md.append(f"| {idx} | {task_desc} | **{owner}** | {deadline} |")
        md.append("")
    else:
        md.append("_No action items assigned._\n")
        
    return "\n".join(md)
