import React, { useState } from 'react';
import { askTutor } from '../api';

export default function TutorView({ onStartQuiz }) {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      text: "Hello! I am your EngineeringAI Tutor. I explain complex engineering concepts step by step, grounded directly in your uploaded course notes with real document citations.\n\nAsk me any concept, formula, or system architecture question to get started!",
      citations: []
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const samplePrompts = [
    "What is the Critical Section problem and how do semaphores solve it?",
    "Explain how the chain rule is used in neural network backpropagation.",
    "What is the difference between a mutex lock and a counting semaphore?",
    "Why can't a single-layer perceptron classify XOR?",
  ];

  const handleSend = async (questionText = null) => {
    const q = questionText || input;
    if (!q.trim() || loading) return;

    const newMsgs = [...messages, { role: 'user', text: q }];
    setMessages(newMsgs);
    setInput('');
    setLoading(true);

    try {
      const data = await askTutor(q);
      setMessages([
        ...newMsgs,
        {
          role: 'assistant',
          text: data.answer || "No response generated.",
          citations: data.citations || []
        }
      ]);
    } catch (err) {
      setMessages([
        ...newMsgs,
        {
          role: 'assistant',
          text: `⚠️ Error retrieving answer: ${err.message}. Please ensure the backend is running.`,
          citations: []
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <span>🎓</span>
          <span>Adaptive AI Engineering Tutor</span>
        </div>
        <p className="card-subtitle">
          Ask questions against your uploaded engineering notes. Every technical claim includes verified document and page number citations.
        </p>

        <div className="prompt-chips">
          {samplePrompts.map((p, idx) => (
            <button key={idx} className="prompt-chip" onClick={() => handleSend(p)}>
              💡 {p}
            </button>
          ))}
        </div>

        <div className="chat-container">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`chat-bubble ${m.role === 'user' ? 'chat-user' : 'chat-ai'}`}
            >
              <div style={{ fontWeight: 600, fontSize: '0.82rem', marginBottom: '0.35rem', color: m.role === 'user' ? '#93c5fd' : '#06b6d4' }}>
                {m.role === 'user' ? '👤 You' : '⚡ EngineeringAI Tutor'}
              </div>
              <div style={{ whiteSpace: 'pre-wrap' }}>{m.text}</div>

              {m.citations && m.citations.length > 0 && (
                <div className="citations-box">
                  <div style={{ fontSize: '0.78rem', fontWeight: 600, color: 'var(--accent-cyan)', marginBottom: '0.4rem' }}>
                    📖 Genuine Course Citations:
                  </div>
                  {m.citations.map((c, cIdx) => (
                    <div key={cIdx} style={{ marginBottom: '0.4rem' }}>
                      <span className="citation-tag">
                        📄 {c.filename} • Page {c.page}
                      </span>
                      <span style={{ fontSize: '0.78rem', color: '#9ca3af' }}>
                        "{c.excerpt}"
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

          {loading && (
            <div className="chat-bubble chat-ai">
              <span style={{ color: 'var(--accent-cyan)' }}>⚡ EngineeringAI is searching course notes and synthesizing answer...</span>
            </div>
          )}
        </div>

        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <input
            type="text"
            className="input-field"
            placeholder="Ask a technical question from your engineering notes..."
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
            Ask Tutor
          </button>
        </div>
      </div>
    </div>
  );
}
