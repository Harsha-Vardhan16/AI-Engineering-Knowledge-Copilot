import React from 'react';

export default function Navbar({ activeTab, setActiveTab, health }) {
  const tabs = [
    { id: 'tutor', label: 'AI Tutor', icon: '🎓' },
    { id: 'quiz', label: 'Adaptive Quiz', icon: '📝' },
    { id: 'dashboard', label: 'Mastery Dashboard', icon: '📊' },
    { id: 'docs', label: 'Course Notes', icon: '📚' },
    { id: 'agent', label: 'AI Agent & MCP', icon: '🤖' },
    { id: 'voice', label: 'Alexa+ Voice', icon: '🎙️' },
  ];

  return (
    <header className="navbar">
      <div className="brand">
        <span style={{ fontSize: '1.4rem' }}>⚡</span>
        <div>
          <span>EngineeringAI</span>
          <span style={{ fontSize: '0.72rem', color: '#9ca3af', marginLeft: '6px' }}>Adaptive Tutor</span>
        </div>
        <span className="brand-badge">Amazon 2026</span>
      </div>

      <nav className="nav-links">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`nav-btn ${activeTab === tab.id ? 'active' : ''}`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </nav>

      <div className="nav-right">
        <div className="health-pill" title={`Ollama: ${health?.ollama_connected ? 'Connected' : 'Offline'} | Indexed Vectors: ${health?.total_faiss_vectors || 0}`}>
          <span className="pulse-dot"></span>
          <span>{health?.ollama_connected ? 'Ollama llama3.2' : 'Backend Ready'}</span>
          <span>•</span>
          <span>{health?.documents_indexed || 0} Docs</span>
        </div>
      </div>
    </header>
  );
}
