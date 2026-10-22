from fastapi import APIRouter
from pydantic import BaseModel, Field
import re
from services.agent_service import run_agent_cycle

router = APIRouter(prefix="/voice", tags=["Voice / Alexa+ Simulator"])


class VoiceSimulateRequest(BaseModel):
    transcript: str = Field(..., description="Spoken utterance or typed fallback input")
    student_id: str = "student_1"


def clean_for_speech(text: str) -> str:
    """
    Cleans markdown formatting and citations for natural voice synthesis.
    """
    # Remove markdown bold/italics
    cleaned = re.sub(r'[*_#`]', '', text)
    # Remove bullet points
    cleaned = re.sub(r'^\s*[-•]\s*', '', cleaned, flags=re.MULTILINE)
    # Remove citation tags like [Doc: ..., Page: ...]
    cleaned = re.sub(r'\[Document:.*?Page:.*?\]', '', cleaned)
    # Remove excessive newlines
    cleaned = re.sub(r'\n+', ' ', cleaned).strip()
    return cleaned


@router.post("/simulate")
def api_voice_simulate(req: VoiceSimulateRequest):
    """
    Alexa+ Conversational Voice Simulator:
    Processes user speech input, executes backend agent & MCP tools,
    and returns voice-ready speech output alongside visual card payload.
    """
    agent_output = run_agent_cycle(user_message=req.transcript, student_id=req.student_id)
    raw_response = agent_output.get("response", "")
    tool_calls = agent_output.get("tool_calls", [])

    speech = clean_for_speech(raw_response)

    # Determine intent for visual card
    intent = "general_qa"
    if tool_calls:
        tool_name = tool_calls[0].get("tool", "")
        if "quiz" in tool_name:
            intent = "quiz_generation"
        elif "progress" in tool_name:
            intent = "progress_review"
        elif "recommend" in tool_name:
            intent = "topic_recommendation"
        elif "plan" in tool_name:
            intent = "study_planning"
        elif "notes" in tool_name:
            intent = "notes_retrieval"

    return {
        "user_transcript": req.transcript,
        "spoken_response": speech[:600],  # Concise speech limit
        "display_card": {
            "title": f"EngineeringAI Voice Skill ({intent.replace('_', ' ').title()})",
            "body": raw_response,
            "tools_invoked": [t.get("tool") for t in tool_calls]
        },
        "tool_calls": tool_calls,
        "alexa_plus_architecture": {
            "protocol": "Model Context Protocol (MCP) Streamable HTTP",
            "compliance_note": "Per official Amazon Hackathon Rules & FAQ, preview Alexa+ SDK tools are gated to select partners; this simulator demonstrates open MCP tool interop."
        }
    }
