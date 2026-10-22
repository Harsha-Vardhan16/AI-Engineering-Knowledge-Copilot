import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar.jsx';
import TutorView from './components/TutorView.jsx';
import QuizView from './components/QuizView.jsx';
import DashboardView from './components/DashboardView.jsx';
import DocumentsView from './components/DocumentsView.jsx';
import AgentView from './components/AgentView.jsx';
import VoiceSimulatorView from './components/VoiceSimulatorView.jsx';
import { checkHealth } from './api';

export default function App() {
  const [activeTab, setActiveTab] = useState('tutor');
  const [health, setHealth] = useState(null);
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const fetchHealth = async () => {
    try {
      const data = await checkHealth();
      setHealth(data);
    } catch (err) {
      console.warn("Backend not reached yet:", err);
    }
  };

  useEffect(() => {
    fetchHealth();
    const interval = setInterval(fetchHealth, 15000);
    return () => clearInterval(interval);
  }, [refreshTrigger]);

  const handleQuizCompleted = () => {
    setRefreshTrigger((prev) => prev + 1);
  };

  const handleStartRemediation = (topic) => {
    setActiveTab('quiz');
  };

  return (
    <div className="app-container">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        health={health}
      />

      <main className="main-content">
        {activeTab === 'tutor' && (
          <TutorView onStartQuiz={() => setActiveTab('quiz')} />
        )}
        {activeTab === 'quiz' && (
          <QuizView onQuizCompleted={handleQuizCompleted} />
        )}
        {activeTab === 'dashboard' && (
          <DashboardView onSelectTopicForQuiz={handleStartRemediation} />
        )}
        {activeTab === 'docs' && (
          <DocumentsView onDocumentsUpdated={() => setRefreshTrigger((p) => p + 1)} />
        )}
        {activeTab === 'agent' && (
          <AgentView />
        )}
        {activeTab === 'voice' && (
          <VoiceSimulatorView />
        )}
      </main>

      <footer style={{ borderTop: '1px solid var(--border-color)', padding: '1.25rem 2rem', textAlign: 'center', fontSize: '0.8rem', color: '#6b7280' }}>
        <span>EngineeringAI — Adaptive Engineering Tutor • Amazon Developer Hackathon 2026: Build, Ship, Shape</span>
        <span style={{ margin: '0 0.5rem' }}>•</span>
        <span>Local Ollama `llama3.2` + Streamable HTTP MCP Server</span>
      </footer>
    </div>
  );
}
