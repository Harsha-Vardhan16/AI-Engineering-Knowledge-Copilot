from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from mcp_server import get_mcp_tools_metadata
from services.agent_service import execute_tool

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol"])


class MCPToolCallRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}


@router.get("/tools")
def api_mcp_list_tools():
    """
    Returns tools list compliant with official MCP 2.x JSON-RPC specification.
    """
    return {
        "tools": get_mcp_tools_metadata()
    }


@router.post("/call")
def api_mcp_call_tool(req: MCPToolCallRequest):
    """
    Direct invocation of MCP tool over HTTP JSON-RPC compliant envelope.
    """
    try:
        result = execute_tool(req.name, req.arguments)
        return {
            "content": [
                {
                    "type": "text",
                    "text": str(result)
                }
            ],
            "isError": False
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Error executing tool {req.name}: {str(e)}"
                }
            ],
            "isError": True
        }
