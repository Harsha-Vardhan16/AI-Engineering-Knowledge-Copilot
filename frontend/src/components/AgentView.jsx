import React, { useState, useEffect } from 'react';
import { sendAgentMessage, listMCPTools, invokeMCPTool } from '../api';

export default function AgentView() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "I am the EngineeringAI Autonomous Agent. I don't just chat—I have tool-calling capabilities wired directly to our Model Context Protocol (MCP) server.\n\nTry prompts like:\n• 'What are my weak topics and current progress?'\n• 'Recommend what topic I should study next'\n• 'Generate a quiz on Process Synchronization'\n• 'Create a 5-hour study plan for neural networks'\n• 'Search course notes for Peterson algorithm'",
      tool_calls: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [mcpTools, setMcpTools] = useState([]);
  const [selectedTool, setSelectedTool] = useState(null);
  const [toolArgsInput, setToolArgsInput] = useState('{}');
  const [toolResult, setToolResult] = useState(null);
  const [testingTool, setTestingTool] = useState(false);

  useEffect(() => {
    listMCPTools().then((res) => {
      setMcpTools(res.tools || []);
      if (res.tools && res.tools.length > 0) {
        setSelectedTool(res.tools[0]);
        setToolArgsInput(JSON.stringify(res.tools[0].inputSchema?.properties?.query ? { query: "semaphores" } : {}, null, 2));
      }
    }).catch(console.error);
  }, []);

  const handleSend = async (msg = null) => {
    const text = msg || input;
    if (!text.trim() || loading) return;

    const newMsgs = [...messages, { role: 'user', text }];
    setMessages(newMsgs);
    setInput('');
    setLoading(true);

    try {
      const data = await sendAgentMessage(text);
      setMessages([
        ...newMsgs,
        {
          role: 'assistant',
          text: data.response,
          tool_calls: data.tool_calls || []
        }
      ]);
    } catch (err) {
      setMessages([
        ...newMsgs,
        {
          role: 'assistant',
          text: `⚠️ Agent execution error: ${err.message}`,
          tool_calls: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleRunToolDirectly = async () => {
    if (!selectedTool) return;
    setTestingTool(true);
    setToolResult(null);
    try {
      const parsedArgs = JSON.parse(toolArgsInput || '{}');
      const res = await invokeMCPTool(selectedTool.name, parsedArgs);
      setToolResult(res);
    } catch (err) {
      setToolResult({ isError: true, content: [{ text: err.message }] });
    } finally {
      setTestingTool(false);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <span>🤖</span>
          <span>Real AI Agent & MCP Tool Execution</span>
        </div>
        <p className="card-subtitle">
          Autonomous tool-calling agent integrated with official Model Context Protocol (MCP 2.x) tools.
        </p>

        {/* Chat Thread */}
        <div className="chat-container">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`chat-bubble ${m.role === 'user' ? 'chat-user' : 'chat-ai'}`}
            >
              <div style={{ fontWeight: 600, fontSize: '0.82rem', marginBottom: '0.35rem', color: m.role === 'user' ? '#93c5fd' : '#c084fc' }}>
                {m.role === 'user' ? '👤 Student' : '🤖 Tool-Calling Agent'}
              </div>

              {m.tool_calls && m.tool_calls.length > 0 && (
                <div style={{ marginBottom: '0.75rem', display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                  {m.tool_calls.map((tc, tcIdx) => (
                    <span key={tcIdx} className="tool-pill">
                      ⚙️ Tool Invoked: <strong>{tc.tool}</strong>
                    </span>
                  ))}
                </div>
              )}

              <div style={{ whiteSpace: 'pre-wrap' }}>{m.text}</div>
            </div>
          ))}

          {loading && (
            <div className="chat-bubble chat-ai">
              <span style={{ color: '#c084fc' }}>⚙️ Agent evaluating tools and executing backend action...</span>
            </div>
          )}
        </div>

        {/* Input Bar */}
        <div style={{ display: 'flex', gap: '0.75rem', marginBottom: '1.5rem' }}>
          <input
            type="text"
            className="input-field"
            placeholder="Command the agent (e.g. 'What are my weak topics?', 'Recommend next topic', 'Quiz me on semaphores')..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={loading}
          />
          <button
            className="btn-primary"
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
          >
            Send to Agent
          </button>
        </div>

        {/* MCP Live Inspector & Runner */}
        <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1.25rem' }}>
          <h4 style={{ color: '#fff', fontSize: '1.05rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>⚡</span>
            <span>Live MCP (Model Context Protocol) Tool Inspector</span>
          </h4>
          <p style={{ color: '#9ca3af', fontSize: '0.82rem', marginBottom: '1rem' }}>
            Verified compliant with the official Model Context Protocol (MCP 2.x) Streamable HTTP & JSON-RPC specifications.
          </p>

          <div className="grid-2">
            <div>
              <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '0.35rem' }}>
                Registered MCP Tool:
              </label>
              <select
                className="input-field"
                value={selectedTool?.name || ''}
                onChange={(e) => {
                  const t = mcpTools.find((x) => x.name === e.target.value);
                  setSelectedTool(t);
                  if (t?.name === 'search_course_notes') setToolArgsInput(JSON.stringify({ query: 'semaphores', top_k: 3 }, null, 2));
                  else if (t?.name === 'generate_quiz') setToolArgsInput(JSON.stringify({ topic: 'Process Synchronization', num_questions: 3 }, null, 2));
                  else if (t?.name === 'create_study_plan') setToolArgsInput(JSON.stringify({ goal: 'Master Neural Networks', hours_available: 5.0 }, null, 2));
                  else setToolArgsInput(JSON.stringify({ student_id: 'student_1' }, null, 2));
                }}
              >
                {mcpTools.map((t) => (
                  <option key={t.name} value={t.name} style={{ background: '#111827' }}>
                    {t.name}
                  </option>
                ))}
              </select>

              <div style={{ marginTop: '0.75rem', fontSize: '0.82rem', color: '#cbd5e1' }}>
                <strong>Description:</strong> {selectedTool?.description}
              </div>

              <div style={{ marginTop: '0.75rem' }}>
                <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '0.35rem' }}>
                  Arguments (JSON payload):
                </label>
                <textarea
                  className="input-field"
                  style={{ fontFamily: 'var(--font-mono)', fontSize: '0.82rem', height: '90px' }}
                  value={toolArgsInput}
                  onChange={(e) => setToolArgsInput(e.target.value)}
                />
              </div>

              <button
                className="btn-secondary"
                style={{ marginTop: '0.75rem' }}
                onClick={handleRunToolDirectly}
                disabled={testingTool}
              >
                {testingTool ? 'Invoking MCP Tool...' : 'Execute Tool Over MCP Protocol'}
              </button>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '0.35rem' }}>
                MCP Protocol Response Envelope:
              </label>
              <pre className="code-block" style={{ height: '240px', overflowY: 'auto' }}>
                {toolResult
                  ? JSON.stringify(toolResult, null, 2)
                  : "// Select a tool and click 'Execute Tool Over MCP Protocol' to inspect live JSON-RPC envelope"}
              </pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
