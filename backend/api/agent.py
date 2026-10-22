from fastapi import APIRouter
from pydantic import BaseModel, Field
from services.agent_service import run_agent_cycle, TOOL_REGISTRY

router = APIRouter(prefix="/agent", tags=["AI Agent"])


class AgentChatRequest(BaseModel):
    message: str = Field(..., description="Student query or command to the agent")
    student_id: str = "student_1"


@router.post("/chat")
def api_agent_chat(req: AgentChatRequest):
    """
    Direct endpoint for autonomous tool-calling AI agent.
    Selects tools, executes them against backend services, and synthesizes answers.
    """
    result = run_agent_cycle(user_message=req.message, student_id=req.student_id)
    return result


@router.get("/tools")
def api_list_tools():
    """
    Lists the registered backend tools available to the AI agent and MCP server.
    """
    return {
        "tools": TOOL_REGISTRY
    }
