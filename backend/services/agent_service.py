import json
import re
from typing import Dict, Any, List

from services.tutor_service import answer_question
from services.adaptive_learning_service import (
    generate_quiz,
    get_learning_progress,
    recommend_next_topic,
    create_study_plan
)
from services.llm_service import query_ollama, generate_llm_response

# Shared tool functions
TOOL_REGISTRY = {
    "search_course_notes": {
        "description": "Searches uploaded engineering notes with real-time semantic retrieval and citations.",
        "parameters": {"query": "string (e.g. 'explain semaphore implementation')"}
    },
    "generate_quiz": {
        "description": "Generates a conceptual engineering quiz grounded in course notes to assess understanding.",
        "parameters": {"topic": "string", "num_questions": "integer (optional, default 3)"}
    },
    "get_learning_progress": {
        "description": "Retrieves the student's actual stored mastery metrics, quiz scores, and weak topics from SQLite.",
        "parameters": {"student_id": "string (optional, default 'student_1')"}
    },
    "recommend_next_topic": {
        "description": "Recommends the next topic to study based on stored mastery scores, prerequisites, and misconceptions.",
        "parameters": {"student_id": "string (optional, default 'student_1')"}
    },
    "create_study_plan": {
        "description": "Generates a structured, milestone-based study plan based on student's goals and weekly hours.",
        "parameters": {"goal": "string", "hours_available": "number (e.g. 6)"}
    }
}


def execute_tool(tool_name: str, args: Dict[str, Any]) -> Any:
    """
    Executes a real backend tool and returns structured data.
    """
    if tool_name == "search_course_notes":
        query = args.get("query") or args.get("question") or "engineering concepts"
        return answer_question(question=query)

    elif tool_name == "generate_quiz":
        topic = args.get("topic")
        num_q = int(args.get("num_questions", 3))
        return generate_quiz(topic=topic, num_questions=num_q)

    elif tool_name == "get_learning_progress":
        student_id = args.get("student_id", "student_1")
        return get_learning_progress(student_id=student_id)

    elif tool_name == "recommend_next_topic":
        student_id = args.get("student_id", "student_1")
        return recommend_next_topic(student_id=student_id)

    elif tool_name == "create_study_plan":
        goal = args.get("goal", "Pass engineering finals with high mastery")
        hours = float(args.get("hours_available", 6.0))
        student_id = args.get("student_id", "student_1")
        return create_study_plan(goal=goal, hours_available=hours, student_id=student_id)

    else:
        raise ValueError(f"Unknown tool: {tool_name}")


def run_agent_cycle(user_message: str, student_id: str = "student_1") -> Dict[str, Any]:
    """
    Autonomous tool-calling agent:
    Parses intent -> selects tool(s) -> executes tool(s) -> synthesizes final response.
    """
    msg_lower = user_message.lower()

    # Rule-assisted + LLM intent classification for maximum reliability
    detected_tool = None
    tool_args = {}

    if any(k in msg_lower for k in ["progress", "how am i doing", "my stats", "my score", "weak topics", "mastery"]):
        detected_tool = "get_learning_progress"
        tool_args = {"student_id": student_id}

    elif any(k in msg_lower for k in ["recommend", "what next", "what should i learn", "what to study", "next topic"]):
        detected_tool = "recommend_next_topic"
        tool_args = {"student_id": student_id}

    elif any(k in msg_lower for k in ["quiz", "test me", "question me", "practice test", "exam"]):
        detected_tool = "generate_quiz"
        # Extract topic from message if mentioned
        topic_match = None
        for t in ["Process Synchronization", "Artificial Neural Networks", "Convolutional Neural Networks", "Database Management Systems", "Semaphores"]:
            if t.lower() in msg_lower:
                topic_match = t
                break
        tool_args = {"topic": topic_match, "num_questions": 3}

    elif any(k in msg_lower for k in ["study plan", "schedule", "plan my week", "routine"]):
        detected_tool = "create_study_plan"
        hours_match = re.search(r'(\d+)\s*hours?', msg_lower)
        hours = float(hours_match.group(1)) if hours_match else 6.0
        tool_args = {"goal": user_message, "hours_available": hours, "student_id": student_id}

    elif any(k in msg_lower for k in ["what is", "how does", "explain", "why", "difference between", "notes say", "formula"]):
        detected_tool = "search_course_notes"
        tool_args = {"query": user_message}

    # If no pattern matched, let Ollama select or answer directly
    executed_tools = []
    if detected_tool:
        result = execute_tool(detected_tool, tool_args)
        executed_tools.append({
            "tool": detected_tool,
            "parameters": tool_args,
            "result": result
        })

        # Synthesize conversational response based on actual tool output
        if detected_tool == "get_learning_progress":
            resp = (
                f"Here is your current stored learning progress:\n\n"
                f"• Overall Mastery: {result.get('overall_mastery')}%\n"
                f"• Quizzes Completed: {result.get('total_quizzes_completed')}\n"
                f"• Average Score: {result.get('average_quiz_score')}%\n\n"
            )
            if result.get("weak_topics"):
                resp += f"⚠️ Topics needing review (<60%): {', '.join(t['topic'] + ' (' + str(t['mastery_score']) + '%)' for t in result['weak_topics'])}\n"
            if result.get("mastered_topics"):
                resp += f"✅ Mastered topics (≥80%): {', '.join(t['topic'] for t in result['mastered_topics'])}\n"
            resp += "\nWould you like me to recommend what to focus on next or generate a targeted quiz?"

        elif detected_tool == "recommend_next_topic":
            resp = (
                f"🎯 **Recommendation**: Focus on **{result.get('recommended_topic')}**.\n\n"
                f"**Why**: {result.get('reason')}\n\n"
                f"**Prerequisites to check**: {', '.join(result.get('prerequisites', []))}\n\n"
                f"**Recommended action**:\n" + "\n".join(result.get("actionable_next_steps", []))
            )

        elif detected_tool == "generate_quiz":
            resp = (
                f"I've generated a new adaptive quiz for you: **{result.get('title')}** "
                f"citing `{result.get('source_document')}` (Page {result.get('page')}).\n"
                f"It contains {result.get('total_questions')} conceptual questions. You can take it directly in the Quiz tab!"
            )

        elif detected_tool == "create_study_plan":
            resp = (
                f"📅 I've created your personalized **{result.get('hours_per_week')} hours/week** study plan for: '{result.get('goal')}'.\n\n"
                f"It includes 3 focused phases addressing weak spots first, followed by concept deepening and voice synthesis. "
                f"View the complete schedule in the Study Plan dashboard."
            )

        elif detected_tool == "search_course_notes":
            resp = result.get("answer", "")

        return {
            "response": resp,
            "tool_calls": executed_tools,
            "agent_state": "executed"
        }

    # Direct conversational fallback
    resp = generate_llm_response(
        prompt=f"User: {user_message}\nAnswer as an engineering tutor:",
        fallback_text="I am your EngineeringAI Tutor. You can ask me to explain course concepts, take a quiz, check your learning progress, recommend your next topic, or generate a personalized study plan."
    )

    return {
        "response": resp,
        "tool_calls": [],
        "agent_state": "direct_response"
    }
