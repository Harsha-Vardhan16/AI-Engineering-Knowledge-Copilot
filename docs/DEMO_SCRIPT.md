# EngineeringAI — 3-Minute Video Demo Script
## Amazon Developer Hackathon 2026: Build, Ship, Shape

**Presenter:** Full-Stack AI Engineer  
**Duration:** Under 3 Minutes (Complies with Devpost Limit)  
**Target Audience:** Amazon Hackathon Judges (Alexa+ & Developer Tools Track)

---

### [0:00 - 0:30] Hook & Problem Statement
* **Screen:** Open browser at `http://localhost:5173`. Show the dark-slate EngineeringAI interface with live health indicator.
* **Spoken Script:**
  > "Hello judges! Most educational chatbots merely summarize PDFs without checking whether a student actually understands the material. For the Amazon Build, Ship, Shape 2026 Hackathon, we built **EngineeringAI**—an adaptive engineering tutor powered by local Ollama, offline FAISS retrieval with genuine page citations, an autonomous tool-calling agent, and an official Model Context Protocol (MCP) server."

---

### [0:30 - 1:00] Step 1: Real RAG with Page Citations
* **Action:** Click on the **Course Notes** tab. Point out the 8 indexed engineering course notes (`OS Unit-3`, `3-ANN Level 1`, `DBMS Unit 3`).
* **Action:** Switch to the **AI Tutor** tab. Click the suggested prompt: *"What is the Critical Section problem and how do semaphores solve it?"*
* **Observation:** The AI Tutor responds with a step-by-step engineering breakdown and highlights genuine citation tags: `[OS Unit-3 Process Synchronization.pdf • Page 4]`.
* **Spoken Script:**
  > "Notice how our RAG pipeline doesn't hallucinate citations. It extracts text page-by-page, embeds it into FAISS, and displays the exact source document and page number for every concept."

---

### [1:00 - 1:45] Step 2: The Adaptive Learning Loop & Misconception Detection
* **Action:** Click **Adaptive Quiz** tab. Select `Process Synchronization` and click **Generate Adaptive Quiz**.
* **Action:** Answer Question 1 correctly (`Mutual Exclusion`) and Question 2 intentionally wrong to demonstrate misconception analysis. Click **Submit Answers & Update Mastery**.
* **Observation:** Score calculates immediately (e.g. 66.7%). The system highlights:
  - Explanations for correct/incorrect choices
  - Detected Misconception: `Semaphores - Review counting vs binary semaphore invariants`.
* **Spoken Script:**
  > "Here is our flagship differentiator: the adaptive learning cycle. When the student submits answers, results are immediately stored in SQLite. It pinpoints the exact technical misconception instead of just marking right or wrong."

---

### [1:45 - 2:15] Step 3: Mastery Dashboard & Personalized Study Plan
* **Action:** Navigate to **Mastery Dashboard**.
* **Observation:**
  - Topic mastery bar for `Process Synchronization` shows updated calculated score (`66.7% • Proficient`).
  - The **Adaptive Recommendation Card** flags: *"Why: Your stored mastery in Process Synchronization is 66.7%. You understand basic principles but need targeted review on semaphore edge cases before advancing."*
  - Point out the 3-phase **Personalized Study Plan** allocating weekly hours to weak topics first.
* **Spoken Script:**
  > "In the dashboard, zero metrics are hardcoded. The system traces our domain prerequisite graph and dynamically recommends the exact topic to study next, complete with a structured weekly study plan."

---

### [2:15 - 2:45] Step 4: Real AI Agent & Official MCP Server
* **Action:** Click **AI Agent & MCP** tab.
* **Action:** Type: *"What are my weak topics and what should I do?"*
* **Observation:** Watch the agent autonomously detect and invoke the `get_learning_progress` tool and return stored database stats.
* **Action:** Scroll down to the **Live MCP Tool Inspector**. Select `recommend_next_topic` and click **Execute Tool Over MCP Protocol**. Show the live JSON-RPC response.
* **Spoken Script:**
  > "Under the hood, we implemented the official Model Context Protocol (MCP 2.x) standard. Our autonomous agent dispatches real backend tools, and external MCP clients can interact with our Streamable HTTP transport."

---

### [2:45 - 3:00] Step 5: Alexa+ Voice Simulator & Wrap-Up
* **Action:** Click **Alexa+ Voice** tab. Click the sample chip: *"Alexa, ask Engineering Tutor how semaphores prevent race conditions."*
* **Observation:** The simulator processes the query, plays natural speech audio, and renders a multimodal card simulating an Echo Show screen.
* **Spoken Script:**
  > "Finally, our voice simulator provides hands-free speech input and audio synthesis, paving the way for conversational devices. EngineeringAI turns static course PDFs into an active, adaptive learning mentor. Thank you!"
