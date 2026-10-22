import sys
import os
import json
import unittest

# Add backend directory to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from database.db import (
    init_db,
    get_all_documents,
    get_student_mastery,
    get_quiz_attempts
)
from vector_store.faiss_store import get_total_vectors
from services.tutor_service import answer_question
from services.adaptive_learning_service import (
    generate_quiz,
    submit_quiz,
    get_learning_progress,
    recommend_next_topic,
    create_study_plan
)
from mcp_server import get_mcp_tools_metadata
from services.agent_service import execute_tool, run_agent_cycle


class TestEngineeringAITutor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        init_db()

    def test_01_backend_health_and_storage(self):
        """Test database and FAISS index readiness"""
        docs = get_all_documents()
        self.assertGreater(len(docs), 0, "Expected at least 1 course document to be indexed in SQLite")
        vectors = get_total_vectors()
        self.assertGreater(vectors, 0, "Expected FAISS index to have stored vectors")
        print(f"\n[PASS] Database & Vector Health: {len(docs)} documents, {vectors} vectors indexed.")

    def test_02_pdf_retrieval_and_genuine_citations(self):
        """Test RAG retrieval and genuine source citations with page numbers"""
        res = answer_question("What is a race condition in process synchronization?")
        self.assertIn("answer", res)
        self.assertIn("citations", res)
        self.assertGreater(len(res["citations"]), 0, "Expected citations from uploaded engineering notes")

        first_cit = res["citations"][0]
        self.assertIn("filename", first_cit)
        self.assertIn("page", first_cit)
        self.assertGreaterEqual(first_cit["page"], 1)
        print(f"[PASS] RAG Citation: Cited '{first_cit['filename']}' on Page {first_cit['page']}")

    def test_03_quiz_generation(self):
        """Test generating an adaptive quiz from course notes"""
        quiz = generate_quiz(topic="Process Synchronization", num_questions=3, student_id="test_student")
        self.assertIn("quiz_id", quiz)
        self.assertIn("questions", quiz)
        self.assertEqual(len(quiz["questions"]), 3)
        self.assertIn("A", quiz["questions"][0]["options"])
        self.assertIn("B", quiz["questions"][0]["options"])
        print(f"[PASS] Quiz Generation: Created quiz '{quiz['title']}' with {len(quiz['questions'])} questions.")
        TestEngineeringAITutor._current_quiz_id = quiz["quiz_id"]

    def test_04_quiz_submission_and_persistence(self):
        """Test quiz evaluation, mistake explanations, and SQLite persistence"""
        quiz_id = getattr(TestEngineeringAITutor, "_current_quiz_id", None)
        self.assertIsNotNone(quiz_id, "Quiz ID must exist from previous test")

        # Submit answers (answering Q1 correctly, Q2 incorrectly to test misconception detection)
        student_answers = {"1": "B", "2": "A", "3": "C"}
        result = submit_quiz(quiz_id=quiz_id, student_answers=student_answers, student_id="test_student")

        self.assertIn("score", result)
        self.assertIn("feedback", result)
        self.assertIn("updated_topic_mastery", result)
        self.assertEqual(len(result["feedback"]), 3)

        # Verify persistence in SQLite
        attempts = get_quiz_attempts(student_id="test_student")
        self.assertGreater(len(attempts), 0, "Expected quiz attempt to be saved in SQLite")
        print(f"[PASS] Quiz Submission & Persistence: Score {result['score']}%, stored in SQLite attempt table.")

    def test_05_topic_mastery_calculation(self):
        """Test topic mastery calculation and status updating"""
        masteries = get_student_mastery(student_id="test_student")
        self.assertGreater(len(masteries), 0, "Expected topic mastery row in SQLite")
        m = masteries[0]
        self.assertIn("mastery_score", m)
        self.assertIn("status", m)
        self.assertIn(m["status"], ["Mastered", "Proficient", "Needs Review"])
        print(f"[PASS] Topic Mastery: Topic '{m['topic']}' mastery calculated at {m['mastery_score']}% ({m['status']})")

    def test_06_personalized_recommendations(self):
        """Test adaptive recommendation engine based on real stored mastery"""
        rec = recommend_next_topic(student_id="test_student")
        self.assertIn("recommended_topic", rec)
        self.assertIn("reason", rec)
        self.assertIn("prerequisites", rec)
        self.assertGreater(len(rec["actionable_next_steps"]), 0)
        self.assertTrue(len(rec["reason"]) > 10, "Expected explanation of why the topic is recommended")
        print(f"[PASS] Adaptive Recommendation: '{rec['recommended_topic']}' recommended. Reason: {rec['reason'][:80]}...")

    def test_07_study_plan_generation(self):
        """Test personalized weekly study plan generation"""
        plan = create_study_plan(goal="Pass Operating Systems Exam", hours_available=6.0, student_id="test_student")
        self.assertIn("schedule", plan)
        self.assertEqual(len(plan["schedule"]), 3)
        self.assertEqual(plan["hours_per_week"], 6.0)
        print(f"[PASS] Study Plan: Created 3-phase schedule for '{plan['goal']}' with {plan['hours_per_week']} hrs/wk.")

    def test_08_mcp_tool_discovery_and_invocation(self):
        """Test MCP tool registry and tool invocation conforming to MCP specification"""
        tools = get_mcp_tools_metadata()
        self.assertEqual(len(tools), 5, "Expected exactly 5 standard MCP tools")
        tool_names = [t["name"] for t in tools]
        self.assertIn("search_course_notes", tool_names)
        self.assertIn("generate_quiz", tool_names)
        self.assertIn("get_learning_progress", tool_names)
        self.assertIn("recommend_next_topic", tool_names)
        self.assertIn("create_study_plan", tool_names)

        # Invoke an MCP tool
        res = execute_tool("get_learning_progress", {"student_id": "test_student"})
        self.assertIn("overall_mastery", res)
        print(f"[PASS] MCP Tool Discovery & Execution: 5 tools verified. Invocation returned valid result.")

    def test_09_agent_autonomous_cycle(self):
        """Test tool-calling agent autonomous cycle"""
        agent_out = run_agent_cycle("What are my weak topics?", student_id="test_student")
        self.assertIn("response", agent_out)
        self.assertIn("tool_calls", agent_out)
        self.assertGreater(len(agent_out["tool_calls"]), 0)
        self.assertEqual(agent_out["tool_calls"][0]["tool"], "get_learning_progress")
        print(f"[PASS] Autonomous AI Agent: Correctly selected tool '{agent_out['tool_calls'][0]['tool']}' and synthesized response.")


if __name__ == "__main__":
    unittest.main()
