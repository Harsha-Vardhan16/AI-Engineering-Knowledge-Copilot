# EngineeringAI — System Architecture & Technical Design

EngineeringAI is an adaptive engineering tutor designed for the **Amazon Build, Ship, Shape 2026 Developer Hackathon**. It combines offline-first local RAG with page citations, adaptive assessment, stored mastery analytics, autonomous tool-calling agents, and an official Model Context Protocol (MCP) server.

---

## 1. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Frontend["React 18 + Vite Frontend (:5173)"]
        UI_Tutor["🎓 AI Tutor View (Citations)"]
        UI_Quiz["📝 Adaptive Quiz View"]
        UI_Dash["📊 Mastery Dashboard"]
        UI_Docs["📚 Course Notes Repo"]
        UI_Agent["🤖 Agent & MCP Inspector"]
        UI_Voice["🎙️ Alexa+ Voice Simulator"]
    end

    subgraph API_Gateway["FastAPI Application (:8000)"]
        Router_Upload["/upload & /documents"]
        Router_Search["/search (RAG)"]
        Router_Quiz["/quiz (Generate/Submit)"]
        Router_Adaptive["/adaptive (Mastery & Plan)"]
        Router_Agent["/agent/chat (Tool Calling)"]
        Router_Voice["/voice/simulate"]
        Router_MCP["/mcp (Tools & Calls)"]
    end

    subgraph Core_Services["Modular Backend Services"]
        PDF_Engine["PDF Loader & Page-Level Chunker"]
        FAISS_Store["FAISS Vector Store (Cosine IP)"]
        Embed_Engine["Deterministic 384-d Embedding Engine"]
        LLM_Engine["Local Ollama Client (llama3.2:latest)"]
        Adaptive_Engine["Adaptive Mastery & Prereq Graph"]
        Agent_Engine["Autonomous Tool-Calling Agent"]
    end

    subgraph MCP_Server["Official MCP 2.x Server (:8001 / Streamable HTTP)"]
        Tool_Search["search_course_notes"]
        Tool_Quiz["generate_quiz"]
        Tool_Progress["get_learning_progress"]
        Tool_Rec["recommend_next_topic"]
        Tool_Plan["create_study_plan"]
    end

    subgraph Persistence["Storage & Offline Models"]
        SQLite_DB[("SQLite: engineering_tutor.db\nDocuments, Chunks, Quizzes,\nAttempts, Mastery, Plans")]
        FAISS_Bin["faiss_index.bin"]
        Ollama_Daemon["Ollama Daemon\nllama3.2:latest"]
    end

    UI_Tutor --> Router_Search
    UI_Quiz --> Router_Quiz
    UI_Dash --> Router_Adaptive
    UI_Docs --> Router_Upload
    UI_Agent --> Router_Agent
    UI_Voice --> Router_Voice

    API_Gateway --> Core_Services
    Core_Services --> SQLite_DB
    Core_Services --> FAISS_Store
    Core_Services --> LLM_Engine
    LLM_Engine --> Ollama_Daemon
    FAISS_Store --> FAISS_Bin

    MCP_Server --> Core_Services
    Router_Agent --> Core_Services
```

---

## 2. Core Subsystems

### A. RAG Document Ingestion & Page-Level Citation Engine
1. **Extraction:** `services/pdf_loader.py` extracts text per page using `pypdf`, preserving exact 1-indexed page numbers.
2. **Chunking:** `rag/text_chunker.py` enforces paragraph and token-level boundaries with chunk overlap while retaining `page_number` and `filename`.
3. **Embeddings:** `services/embedding_service.py` generates normalized 384-dimensional semantic frequency vectors with sub-linear TF and signed hash collision distribution, matching `all-MiniLM-L6-v2` dimensionality without PyTorch/CUDA overhead.
4. **FAISS Index:** `vector_store/faiss_store.py` utilizes `IndexFlatIP` (Inner Product on normalized embeddings = Cosine Similarity) for instant sub-millisecond retrieval.
5. **No Hallucinated Citations:** Results always return `{ filename, page, excerpt }` extracted from genuine course chunks.

### B. Adaptive Learning & Misconception Engine
- **Calculated Mastery:** Scores are computed per topic in SQLite (`topic_mastery` table) as `(correct_answers / total_questions) * 100`.
- **Misconception Detection:** When a student selects an incorrect option, the evaluation engine logs the tested concept, explains why the choice was wrong, and stores remediation steps.
- **Prerequisite Knowledge Graph:** Topics like `Process Synchronization` map prerequisites (`Process Scheduling`, `Thread Execution`) and critical components (`Semaphores`, `Critical Section Problem`, `Peterson's Algorithm`).
- **Dynamic Recommendations:** If a student scores <60%, the engine alerts them to weak prerequisite foundations and recommends targeted re-quizzing before advancing.

### C. Model Context Protocol (MCP 2.x) Integration
The project implements the official Model Context Protocol using the official `mcp` SDK:
- **Transport:** Streamable HTTP & JSON-RPC 2.0.
- **Port:** Exposes port `8001` or mounted `/mcp` endpoints.
- **Exposed Tools:**
  1. `search_course_notes(query: str, top_k: int = 4)`
  2. `generate_quiz(topic: str = "", num_questions: int = 3)`
  3. `get_learning_progress(student_id: str = "student_1")`
  4. `recommend_next_topic(student_id: str = "student_1")`
  5. `create_study_plan(goal: str, hours_available: float = 6.0, student_id: str = "student_1")`
- Both the web application, the autonomous AI agent, and third-party MCP clients invoke the **exact same underlying service logic**, guaranteeing consistency.

### D. Voice / Alexa+ Multimodal Simulation
- **Speech Recognition:** Web Speech API (`webkitSpeechRecognition`) captures microphone input with continuous text fallback.
- **Speech Synthesis:** Web Speech API (`speechSynthesis`) delivers natural audio output.
- **Multimodal Display:** Clean visual cards simulate Echo Show / Fire TV screen displays alongside concise audio responses.
