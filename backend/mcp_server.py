import os
import sys
import json
import asyncio
from typing import Optional

# Ensure backend root is in sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from mcp.server.mcpserver import MCPServer
from services.tutor_service import answer_question
from services.adaptive_learning_service import (
    generate_quiz as svc_generate_quiz,
    get_learning_progress as svc_get_learning_progress,
    recommend_next_topic as svc_recommend_next_topic,
    create_study_plan as svc_create_study_plan
)

# Initialize official Model Context Protocol server
mcp = MCPServer(
    name="EngineeringAI-MCP-Server",
    version="1.0.0",
    instructions="Official MCP Server for EngineeringAI: Adaptive Engineering Tutor. Exposes real RAG, quiz generation, mastery tracking, topic recommendation, and study planning."
)


@mcp.tool()
def search_course_notes(query: str, top_k: int = 4) -> str:
    """
    Search indexed engineering course notes with real semantic retrieval and genuine citations.
    """
    result = answer_question(question=query, top_k=top_k)
    return json.dumps(result, indent=2)


@mcp.tool()
def generate_quiz(topic: str = "", num_questions: int = 3) -> str:
    """
    Generate an adaptive engineering quiz grounded in course notes to evaluate student comprehension.
    """
    result = svc_generate_quiz(topic=topic if topic else None, num_questions=num_questions)
    return json.dumps(result, indent=2)


@mcp.tool()
def get_learning_progress(student_id: str = "student_1") -> str:
    """
    Retrieve stored student learning progress, quiz scores, and weak vs mastered topics from SQLite.
    """
    result = svc_get_learning_progress(student_id=student_id)
    return json.dumps(result, indent=2)


@mcp.tool()
def recommend_next_topic(student_id: str = "student_1") -> str:
    """
    Analyze stored topic mastery and recommend the next topic to study with prerequisite explanation.
    """
    result = svc_recommend_next_topic(student_id=student_id)
    return json.dumps(result, indent=2)


@mcp.tool()
def create_study_plan(goal: str = "Master Core Engineering Modules", hours_available: float = 6.0, student_id: str = "student_1") -> str:
    """
    Create a personalized weekly study plan grounded in actual weak topics and available study hours.
    """
    result = svc_create_study_plan(goal=goal, hours_available=hours_available, student_id=student_id)
    return json.dumps(result, indent=2)


def get_mcp_tools_metadata():
    """
    Helper for FastAPI / web simulator to inspect MCP tool definitions conforming to the MCP spec.
    """
    return [
        {
            "name": "search_course_notes",
            "description": "Search indexed engineering course notes with real semantic retrieval and genuine citations.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The concept or question to search in notes"},
                    "top_k": {"type": "integer", "description": "Number of chunks to retrieve", "default": 4}
                },
                "required": ["query"]
            }
        },
        {
            "name": "generate_quiz",
            "description": "Generate an adaptive engineering quiz grounded in course notes to evaluate student comprehension.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "Topic or module name (e.g. 'Process Synchronization')"},
                    "num_questions": {"type": "integer", "description": "Number of questions", "default": 3}
                }
            }
        },
        {
            "name": "get_learning_progress",
            "description": "Retrieve stored student learning progress, quiz scores, and weak vs mastered topics from SQLite.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student identifier", "default": "student_1"}
                }
            }
        },
        {
            "name": "recommend_next_topic",
            "description": "Analyze stored topic mastery and recommend the next topic to study with prerequisite explanation.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "student_id": {"type": "string", "description": "Student identifier", "default": "student_1"}
                }
            }
        },
        {
            "name": "create_study_plan",
            "description": "Create a personalized weekly study plan grounded in actual weak topics and available study hours.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "goal": {"type": "string", "description": "Learning goal or exam objective"},
                    "hours_available": {"type": "number", "description": "Weekly study hours available", "default": 6.0},
                    "student_id": {"type": "string", "description": "Student identifier", "default": "student_1"}
                },
                "required": ["goal"]
            }
        }
    ]


if __name__ == "__main__":
    import uvicorn
    # When executed directly, launch streamable HTTP MCP server on port 8001
    port = int(os.getenv("MCP_PORT", 8001))
    print(f"Starting EngineeringAI Streamable HTTP MCP Server on port {port}...")
    app = mcp.streamable_http_app()
    uvicorn.run(app, host="127.0.0.1", port=port)
