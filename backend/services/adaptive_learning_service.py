import uuid
import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime

from database.db import (
    save_quiz,
    get_quiz_by_id,
    record_quiz_attempt,
    get_student_mastery,
    get_quiz_attempts,
    save_study_plan,
    get_latest_study_plan,
    get_all_chunks_raw,
    get_all_documents
)
from services.embedding_service import create_embeddings
from vector_store.faiss_store import search, get_total_vectors
from database.db import get_chunks_by_indices
from services.llm_service import query_ollama, generate_llm_response


# Prerequisite Knowledge Graph for Engineering Domains
PREREQUISITES_MAP = {
    "Process Synchronization": {
        "prereqs": ["Process Scheduling", "Thread Execution", "Mutual Exclusion"],
        "critical_concepts": ["Semaphores", "Mutex Locks", "Critical Section Problem", "Peterson's Algorithm", "Deadlock Prevention"],
        "next_advancements": ["Deadlock Avoidance (Banker's Algorithm)", "Distributed Synchronization"]
    },
    "Artificial Neural Networks": {
        "prereqs": ["Matrix Multiplication", "Activation Functions", "Gradient Descent"],
        "critical_concepts": ["Perceptron", "Backpropagation", "Loss Functions", "Multi-Layer Perceptron (MLP)"],
        "next_advancements": ["Convolutional Neural Networks (CNN)", "Recurrent Neural Networks (RNN)"]
    },
    "Convolutional Neural Networks": {
        "prereqs": ["Artificial Neural Networks", "Kernel Convolutions", "Feature Mapping"],
        "critical_concepts": ["Stride & Padding", "Pooling Layers (MaxPooling)", "Flattening & Dense Layers"],
        "next_advancements": ["Residual Networks (ResNet)", "Object Detection (YOLO)"]
    },
    "Database Management Systems": {
        "prereqs": ["Relational Algebra", "SQL Basics", "Functional Dependencies"],
        "critical_concepts": ["Normalization (1NF, 2NF, 3NF, BCNF)", "ACID Properties", "Concurrency Control"],
        "next_advancements": ["Two-Phase Locking (2PL)", "Distributed Transactions"]
    },
    "Probability & Statistics": {
        "prereqs": ["Set Theory", "Calculus Integration"],
        "critical_concepts": ["Random Variables", "Probability Density Functions (PDF)", "Bayes' Theorem"],
        "next_advancements": ["Joint Probability Distributions", "Central Limit Theorem"]
    }
}


def _infer_topic_from_text(text: str) -> str:
    text_lower = text.lower()
    if any(k in text_lower for k in ["synchronization", "semaphore", "mutex", "critical section", "process"]):
        return "Process Synchronization"
    if any(k in text_lower for k in ["neural", "perceptron", "backpropagation", "layer", "ann"]):
        return "Artificial Neural Networks"
    if any(k in text_lower for k in ["convolution", "cnn", "pooling", "filter", "kernel"]):
        return "Convolutional Neural Networks"
    if any(k in text_lower for k in ["dbms", "database", "sql", "normalization", "relation", "transaction"]):
        return "Database Management Systems"
    if any(k in text_lower for k in ["probability", "variance", "distribution", "random variable"]):
        return "Probability & Statistics"
    return "Engineering Fundamentals"


def generate_quiz(topic: Optional[str] = None, num_questions: int = 3, student_id: str = "student_1") -> Dict[str, Any]:
    """
    Generates an adaptive quiz from course notes.
    Grounds questions in real document content and records the quiz in DB.
    """
    # 1. Determine target topic if not given
    all_chunks = get_all_chunks_raw()
    all_docs = get_all_documents()

    if not topic:
        # Check student's weakest topic
        mastery_list = get_student_mastery(student_id)
        weak_topics = [m for m in mastery_list if m["mastery_score"] < 60]
        if weak_topics:
            topic = weak_topics[0]["topic"]
        elif all_docs:
            topic = all_docs[0].get("topic", "Process Synchronization")
        else:
            topic = "Process Synchronization"

    # 2. Retrieve relevant context for this topic
    matched_chunks = []
    if get_total_vectors() > 0:
        query_emb = create_embeddings([f"{topic} concepts principles mechanisms definition"])
        indices = search(query_emb, k=5)
        if indices is not None and len(indices) > 0 and len(indices[0]) > 0:
            valid_indices = [int(i) for i in indices[0] if i >= 0]
            matched_chunks = get_chunks_by_indices(valid_indices)

    if not matched_chunks and all_chunks:
        # Filter chunks by topic match
        matched_chunks = [c for c in all_chunks if topic.lower() in c.get("content", "").lower()][:4]
        if not matched_chunks:
            matched_chunks = all_chunks[:3]

    doc_filename = matched_chunks[0].get("filename", "CourseNotes.pdf") if matched_chunks else "Engineering Notes"
    page_num = matched_chunks[0].get("page_number", 1) if matched_chunks else 1
    context_text = "\n\n".join([c.get("content", "")[:400] for c in matched_chunks]) if matched_chunks else "Fundamental engineering principles."

    # 3. Request LLM to produce structured questions
    system_prompt = (
        "You are an engineering assessment generator. "
        "Generate a rigorous multiple choice quiz testing deep conceptual understanding. "
        "Return ONLY a valid JSON array of question objects."
    )

    prompt = f"""
Topic: {topic}
Reference Course Content:
{context_text}

Generate {num_questions} multiple choice questions strictly based on this content.
Format your output as a raw JSON array matching this exact schema:
[
  {{
    "id": 1,
    "question": "Question text here?",
    "options": {{
      "A": "Option text 1",
      "B": "Option text 2",
      "C": "Option text 3",
      "D": "Option text 4"
    }},
    "correct_option": "B",
    "explanation": "Clear explanation of why B is correct and common misconception.",
    "concept_tested": "Key concept keyword"
  }}
]
"""
    raw_response = query_ollama(prompt, system=system_prompt, temperature=0.3)
    questions = []

    if raw_response:
        try:
            # Extract JSON array using regex
            match = re.search(r'\[\s*\{.*\}\s*\]', raw_response, re.DOTALL)
            if match:
                questions = json.loads(match.group(0))
        except Exception as e:
            print(f"Error parsing Ollama quiz JSON: {e}")

    # Fallback to high quality deterministic domain questions if LLM response was incomplete
    if not questions or len(questions) == 0:
        if "sync" in topic.lower() or "process" in topic.lower():
            questions = [
                {
                    "id": 1,
                    "question": "In operating systems, which condition must be met to ensure two processes never execute their critical sections simultaneously?",
                    "options": {
                        "A": "Progress condition",
                        "B": "Mutual Exclusion",
                        "C": "Bounded Waiting",
                        "D": "Aging"
                    },
                    "correct_option": "B",
                    "explanation": "Mutual Exclusion guarantees that if process Pi is executing in its critical section, no other processes can execute in their critical sections.",
                    "concept_tested": "Mutual Exclusion"
                },
                {
                    "id": 2,
                    "question": "What is the primary difference between a binary semaphore and a counting semaphore?",
                    "options": {
                        "A": "Binary semaphores are implemented in hardware; counting semaphores in software",
                        "B": "Binary semaphore values range between 0 and 1, whereas counting semaphores can range over an unrestricted integer domain",
                        "C": "Counting semaphores cause busy waiting, while binary semaphores do not",
                        "D": "Binary semaphores can only be used by two processes maximum"
                    },
                    "correct_option": "B",
                    "explanation": "A binary semaphore takes values only 0 or 1 (functioning identically to a mutex lock), whereas a counting semaphore's value can range over an unrestricted integer domain across finite resource instances.",
                    "concept_tested": "Semaphores"
                },
                {
                    "id": 3,
                    "question": "Which of the following is NOT one of the four necessary Coffman conditions for a deadlock to occur?",
                    "options": {
                        "A": "Mutual Exclusion",
                        "B": "Hold and Wait",
                        "C": "Preemption allowed",
                        "D": "Circular Wait"
                    },
                    "correct_option": "C",
                    "explanation": "No preemption is the deadlock condition. If preemption is allowed, resources can be forcibly allocated, breaking the deadlock state.",
                    "concept_tested": "Deadlock Conditions"
                }
            ]
        elif "neural" in topic.lower() or "ann" in topic.lower():
            questions = [
                {
                    "id": 1,
                    "question": "What mathematical rule is the foundation of the Backpropagation algorithm in multi-layer neural networks?",
                    "options": {
                        "A": "Euler's formula",
                        "B": "The Chain Rule of calculus",
                        "C": "Bayes' theorem",
                        "D": "L'Hôpital's rule"
                    },
                    "correct_option": "B",
                    "explanation": "Backpropagation relies directly on the Chain Rule of calculus to compute partial derivatives of the loss function with respect to weights across earlier layers.",
                    "concept_tested": "Backpropagation"
                },
                {
                    "id": 2,
                    "question": "Why cannot a single-layer perceptron solve the XOR problem?",
                    "options": {
                        "A": "It lacks a non-linear activation function and XOR is not linearly separable",
                        "B": "It has too many inputs",
                        "C": "Gradient descent diverges on Boolean inputs",
                        "D": "Its learning rate must be negative"
                    },
                    "correct_option": "A",
                    "explanation": "A single-layer perceptron creates a linear decision boundary (hyperplane). Because the XOR function is non-linearly separable, at least one hidden layer or non-linear mapping is required.",
                    "concept_tested": "Linear Separability"
                },
                {
                    "id": 3,
                    "question": "What problem does the ReLU (Rectified Linear Unit) activation function primarily mitigate compared to Sigmoid during deep network training?",
                    "options": {
                        "A": "Overfitting",
                        "B": "Vanishing gradient problem for positive activations",
                        "C": "Curse of dimensionality",
                        "D": "High computational complexity of logarithms"
                    },
                    "correct_option": "B",
                    "explanation": "Sigmoid saturates at both tails with derivatives near zero, causing gradients to vanish. ReLU has a constant derivative of 1 for all positive inputs, preventing vanishing gradients.",
                    "concept_tested": "Activation Functions"
                }
            ]
        else:
            questions = [
                {
                    "id": 1,
                    "question": f"Which foundational principle is primary when analyzing {topic}?",
                    "options": {
                        "A": "Empirical observation without formal verification",
                        "B": "Mathematical consistency, correctness guarantees, and efficiency tradeoffs",
                        "C": "Minimizing hardware redundancy exclusively",
                        "D": "Heuristic approximations only"
                    },
                    "correct_option": "B",
                    "explanation": "Engineering systems require verifiable correctness guarantees alongside quantitative trade-off analysis.",
                    "concept_tested": f"{topic} Foundations"
                },
                {
                    "id": 2,
                    "question": f"In {topic}, what metric best evaluates system reliability?",
                    "options": {
                        "A": "Peak clock frequency",
                        "B": "Mean Time Between Failures (MTBF) and fault tolerance bounds",
                        "C": "Code size in lines",
                        "D": "Number of active threads"
                    },
                    "correct_option": "B",
                    "explanation": "Reliability is formally measured through fault-tolerance bounds and operational availability.",
                    "concept_tested": "Reliability"
                }
            ]

    quiz_id = f"quiz_{uuid.uuid4().hex[:8]}"
    quiz_title = f"{topic} Mastery Check"

    # Save to SQLite
    save_quiz(
        quiz_id=quiz_id,
        topic=topic,
        doc_filename=doc_filename,
        title=quiz_title,
        questions=questions
    )

    # Return client-safe questions (with questions and options)
    client_questions = []
    for q in questions:
        client_questions.append({
            "id": q.get("id"),
            "question": q.get("question"),
            "options": q.get("options"),
            "concept_tested": q.get("concept_tested", topic)
        })

    return {
        "quiz_id": quiz_id,
        "title": quiz_title,
        "topic": topic,
        "source_document": doc_filename,
        "page": page_num,
        "questions": client_questions,
        "total_questions": len(questions)
    }


def submit_quiz(quiz_id: str, student_answers: Dict[str, str], student_id: str = "student_1") -> Dict[str, Any]:
    """
    Evaluates quiz submissions, explains mistakes, identifies misconceptions,
    persists results to SQLite, and updates stored topic mastery.
    """
    quiz = get_quiz_by_id(quiz_id)
    if not quiz:
        raise ValueError(f"Quiz '{quiz_id}' not found.")

    questions = quiz.get("questions", [])
    topic = quiz.get("topic", "General Engineering")
    total_questions = len(questions)
    correct_count = 0
    feedback_list = []
    detected_misconceptions = []

    for q in questions:
        q_id = str(q.get("id"))
        correct_opt = q.get("correct_option", "A").upper().strip()
        student_opt = str(student_answers.get(q_id, "")).upper().strip()
        is_correct = (student_opt == correct_opt)

        if is_correct:
            correct_count += 1
            feedback_list.append({
                "question_id": q_id,
                "question": q.get("question"),
                "student_answer": student_opt,
                "correct_answer": correct_opt,
                "is_correct": True,
                "explanation": q.get("explanation", "Correct understanding demonstrated!")
            })
        else:
            concept = q.get("concept_tested", topic)
            detected_misconceptions.append({
                "concept": concept,
                "question": q.get("question"),
                "student_answer": student_opt,
                "correct_answer": correct_opt,
                "remediation": q.get("explanation", "Review the underlying theorems.")
            })
            feedback_list.append({
                "question_id": q_id,
                "question": q.get("question"),
                "student_answer": student_opt or "Unanswered",
                "correct_answer": correct_opt,
                "is_correct": False,
                "explanation": f"Incorrect. The correct answer is {correct_opt}. {q.get('explanation')}"
            })

    score = round((correct_count / total_questions) * 100, 1) if total_questions > 0 else 0.0
    attempt_id = f"attempt_{uuid.uuid4().hex[:8]}"

    # Persist in SQLite
    record_quiz_attempt(
        attempt_id=attempt_id,
        quiz_id=quiz_id,
        topic=topic,
        student_id=student_id,
        score=score,
        total_questions=total_questions,
        correct_count=correct_count,
        answers=student_answers,
        feedback=feedback_list
    )

    # Fetch updated mastery
    mastery_list = get_student_mastery(student_id)
    current_topic_mastery = next((m for m in mastery_list if m["topic"] == topic), None)
    new_mastery_score = current_topic_mastery["mastery_score"] if current_topic_mastery else score

    return {
        "attempt_id": attempt_id,
        "quiz_id": quiz_id,
        "topic": topic,
        "score": score,
        "correct_count": correct_count,
        "total_questions": total_questions,
        "updated_topic_mastery": new_mastery_score,
        "status": "Mastered" if new_mastery_score >= 80 else ("Proficient" if new_mastery_score >= 60 else "Needs Review"),
        "feedback": feedback_list,
        "detected_misconceptions": detected_misconceptions
    }


def get_learning_progress(student_id: str = "student_1") -> Dict[str, Any]:
    """
    Returns actual stored mastery metrics, quiz history, and weak vs strong topics.
    Zero fabricated numbers.
    """
    masteries = get_student_mastery(student_id)
    attempts = get_quiz_attempts(student_id, limit=10)

    total_attempts = len(attempts)
    avg_score = round(sum(a["score"] for a in attempts) / total_attempts, 1) if total_attempts > 0 else 0.0

    weak_topics = [m for m in masteries if m["mastery_score"] < 60]
    proficient_topics = [m for m in masteries if 60 <= m["mastery_score"] < 80]
    mastered_topics = [m for m in masteries if m["mastery_score"] >= 80]

    overall_mastery = round(sum(m["mastery_score"] for m in masteries) / len(masteries), 1) if masteries else 0.0

    return {
        "student_id": student_id,
        "overall_mastery": overall_mastery,
        "average_quiz_score": avg_score,
        "total_quizzes_completed": total_attempts,
        "topics": masteries,
        "weak_topics": weak_topics,
        "proficient_topics": proficient_topics,
        "mastered_topics": mastered_topics,
        "recent_attempts": attempts
    }


def recommend_next_topic(student_id: str = "student_1") -> Dict[str, Any]:
    """
    Adaptive Recommendation Engine:
    Evaluates real stored topic mastery, traces prerequisites, and explains
    EXACTLY why a topic is recommended with concrete next actions.
    """
    masteries = get_student_mastery(student_id)
    all_docs = get_all_documents()

    # Identify candidate topic
    target_topic = None
    reason = ""
    prerequisites = []
    remediation_steps = []

    # Priority 1: Student has an active topic with score < 60%
    weak = [m for m in masteries if m["mastery_score"] < 60]
    if weak:
        # Sort by lowest score first
        weak.sort(key=lambda x: x["mastery_score"])
        candidate = weak[0]
        target_topic = candidate["topic"]
        score = candidate["mastery_score"]
        attempts = candidate["total_attempts"]
        reason = (
            f"Your stored mastery in '{target_topic}' is {score}% after {attempts} quiz attempt(s). "
            f"You demonstrated critical gaps or misconceptions in core definitions. Reinforcing this topic "
            f"now is required before advancing to dependent higher-level topics."
        )
    # Priority 2: Student has proficient topics (60-80%) that need consolidation
    elif any(60 <= m["mastery_score"] < 80 for m in masteries):
        candidate = next(m for m in masteries if 60 <= m["mastery_score"] < 80)
        target_topic = candidate["topic"]
        reason = (
            f"Your mastery in '{target_topic}' is at {candidate['mastery_score']}%. "
            f"You understand the fundamental principles but need targeted practice on edge cases to achieve full mastery (>80%)."
        )
    # Priority 3: All current topics are mastered or no quizzes taken yet -> Suggest first uploaded course note
    else:
        if all_docs:
            target_topic = all_docs[0].get("topic", "Process Synchronization")
            reason = f"New course module detected from '{all_docs[0]['filename']}'. Let's establish your foundational baseline."
        else:
            target_topic = "Process Synchronization"
            reason = "Recommended starting baseline for Operating Systems and concurrent system engineering."

    # Look up prerequisites from domain knowledge graph
    domain_info = PREREQUISITES_MAP.get(target_topic, {
        "prereqs": ["Foundational Mathematics", "Algorithm Analysis"],
        "critical_concepts": ["Core Definitions", "System Invariants"],
        "next_advancements": ["Advanced Engineering Application"]
    })

    prerequisites = domain_info.get("prereqs", [])
    critical_concepts = domain_info.get("critical_concepts", [])

    remediation_steps = [
        f"1. Review uploaded notes for '{target_topic}' focusing on {', '.join(critical_concepts[:3])}.",
        f"2. Use the AI Tutor to clarify questions with citations.",
        f"3. Retake a 3-question adaptive quiz to lift your mastery score above 80%."
    ]

    return {
        "recommended_topic": target_topic,
        "reason": reason,
        "prerequisites": prerequisites,
        "key_concepts_to_master": critical_concepts,
        "actionable_next_steps": remediation_steps,
        "suggested_quiz_ready": True
    }


def create_study_plan(goal: str, hours_available: float = 6.0, student_id: str = "student_1") -> Dict[str, Any]:
    """
    Creates a personalized milestone-based study plan grounded in actual weak topics
    and available weekly study hours. Persisted in SQLite.
    """
    progress = get_learning_progress(student_id)
    weak = progress.get("weak_topics", [])
    proficient = progress.get("proficient_topics", [])

    plan_id = f"plan_{uuid.uuid4().hex[:8]}"

    # Distribute hours across modules
    hours_per_session = round(hours_available / 3.0, 1)

    schedule = [
        {
            "phase": "Phase 1: Remediation & Weak Topics",
            "hours_allocated": hours_per_session,
            "focus_topics": [w["topic"] for w in weak] if weak else ["Foundational Review"],
            "activities": [
                "Ask AI Tutor targeted questions citing uploaded course notes",
                "Work through step-by-step mathematical or architectural derivations",
                "Resolve identified misconceptions from prior quiz attempts"
            ],
            "milestone": "Achieve >= 70% on targeted re-quizzing"
        },
        {
            "phase": "Phase 2: Core Concept Deepening",
            "hours_allocated": hours_per_session,
            "focus_topics": [p["topic"] for p in proficient] if proficient else ["Core Engineering Modules"],
            "activities": [
                "Examine edge cases and system design tradeoffs",
                "Practice problem sets with citation-backed validation",
                "Complete full-length concept checks"
            ],
            "milestone": "Mastery score across all core modules reaches >= 80%"
        },
        {
            "phase": "Phase 3: Integration & Voice Drill Simulator",
            "hours_allocated": hours_per_session,
            "focus_topics": ["End-to-End Synthesis"],
            "activities": [
                "Use the Alexa+ / Voice simulator for hands-free verbal technical Q&A",
                "Synthesize concepts across course modules",
                "Final readiness assessment"
            ],
            "milestone": "Complete exam or project readiness milestone"
        }
    ]

    plan_data = {
        "plan_id": plan_id,
        "student_id": student_id,
        "goal": goal,
        "hours_per_week": hours_available,
        "created_at": datetime.now().isoformat(),
        "summary": f"Personalized {hours_available}h/week engineering study path designed for: '{goal}'.",
        "schedule": schedule
    }

    save_study_plan(plan_id, student_id, goal, hours_available, plan_data)

    return plan_data
