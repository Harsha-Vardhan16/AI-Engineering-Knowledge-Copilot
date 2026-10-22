import React, { useState, useEffect } from 'react';
import { simulateVoice } from '../api';

export default function VoiceSimulatorView() {
  const [transcript, setTranscript] = useState('');
  const [listening, setListening] = useState(false);
  const [loading, setLoading] = useState(false);
  const [voiceResult, setVoiceResult] = useState(null);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [recognitionSupported, setRecognitionSupported] = useState(false);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      setRecognitionSupported(true);
    }
  }, []);

  const speakText = (text) => {
    if (!ttsEnabled || !('speechSynthesis' in window)) return;
    window.speechSynthesis.cancel(); // Stop prior speech
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  };

  const handleStartVoice = () => {
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRec) {
      alert("Browser speech recognition not supported in this browser. Please type in the input below.");
      return;
    }

    const recognition = new SpeechRec();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setListening(true);
    recognition.onend = () => setListening(false);
    recognition.onerror = (e) => {
      console.error(e);
      setListening(false);
    };

    recognition.onresult = (event) => {
      const speechToText = event.results[0][0].transcript;
      setTranscript(speechToText);
      handleProcessVoice(speechToText);
    };

    recognition.start();
  };

  const handleProcessVoice = async (utterance = null) => {
    const query = utterance || transcript;
    if (!query.trim() || loading) return;

    setLoading(true);
    try {
      const data = await simulateVoice(query);
      setVoiceResult(data);
      if (data.spoken_response) {
        speakText(data.spoken_response);
      }
    } catch (err) {
      alert("Voice simulation error: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const sampleVoicePrompts = [
    "Alexa, ask Engineering Tutor how semaphores prevent race conditions.",
    "Alexa, ask Engineering Tutor for my learning progress.",
    "Alexa, ask Engineering Tutor what topic I should study next.",
    "Alexa, ask Engineering Tutor to quiz me on Neural Networks."
  ];

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <span>🎙️</span>
          <span>Alexa+ Conversational Voice Simulator</span>
        </div>
        <p className="card-subtitle">
          Voice-first multimodal conversational interface invoking real MCP tools and backend agent services.
        </p>

        {/* Hackathon Compliance Notice */}
        <div className="banner">
          <span>ℹ️</span>
          <div>
            <strong>Hackathon Compliance (Amazon Build, Ship, Shape 2026):</strong> The preview Alexa+ SDK tools are restricted to select partners per the official Devpost FAQ. This custom simulator follows the approved track path by running an open <strong>Model Context Protocol (MCP) server</strong> with real-time tool dispatch over HTTP.
          </div>
        </div>

        {/* Quick Voice Chips */}
        <div className="prompt-chips">
          {sampleVoicePrompts.map((p, idx) => (
            <button
              key={idx}
              className="prompt-chip"
              onClick={() => {
                setTranscript(p);
                handleProcessVoice(p);
              }}
            >
              🗣️ {p}
            </button>
          ))}
        </div>

        {/* Voice Input Controls */}
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center', marginBottom: '1.5rem', background: 'rgba(255,255,255,0.02)', padding: '1.25rem', borderRadius: '12px' }}>
          <button
            className={listening ? 'btn-primary' : 'btn-secondary'}
            onClick={handleStartVoice}
            disabled={loading}
            style={{ minWidth: '160px', borderColor: listening ? '#f43f5e' : undefined, background: listening ? 'rgba(244,63,94,0.2)' : undefined }}
          >
            <span>{listening ? '🔴' : '🎤'}</span>
            <span>{listening ? 'Listening...' : 'Voice Input (Mic)'}</span>
          </button>

          <input
            type="text"
            className="input-field"
            placeholder="Or type voice query here (always supported as fallback)..."
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleProcessVoice()}
          />

          <button
            className="btn-primary"
            onClick={() => handleProcessVoice()}
            disabled={loading || !transcript.trim()}
          >
            {loading ? 'Processing...' : 'Simulate Voice'}
          </button>

          <button
            className="btn-secondary"
            title="Toggle Text-to-Speech output"
            onClick={() => {
              setTtsEnabled(!ttsEnabled);
              if (ttsEnabled) window.speechSynthesis?.cancel();
            }}
          >
            <span>{ttsEnabled ? '🔊 Audio ON' : '🔇 Audio Muted'}</span>
          </button>
        </div>

        {/* Multimodal Screen Display (Echo Show Simulator) */}
        {voiceResult && (
          <div className="alexa-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: '0.75rem', marginBottom: '1rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <span style={{ fontSize: '1.4rem' }}>📺</span>
                <div>
                  <h4 style={{ color: '#fff', fontSize: '1.05rem' }}>{voiceResult.display_card?.title}</h4>
                  <span style={{ fontSize: '0.75rem', color: '#06b6d4' }}>Multimodal Echo Show Surface</span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '0.4rem' }}>
                {voiceResult.display_card?.tools_invoked?.map((t, idx) => (
                  <span key={idx} className="tool-pill">
                    ⚙️ {t}
                  </span>
                ))}
              </div>
            </div>

            {/* Speech Output Box */}
            <div style={{ background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.3)', borderRadius: '10px', padding: '1rem', marginBottom: '1rem' }}>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#38bdf8', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                🔊 Alexa+ Spoken Response:
              </div>
              <div style={{ fontSize: '0.98rem', color: '#f8fafc', lineHeight: '1.5' }}>
                "{voiceResult.spoken_response}"
              </div>
            </div>

            {/* Visual Card Payload */}
            <div>
              <div style={{ fontSize: '0.78rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', marginBottom: '0.35rem' }}>
                🖥️ Screen Details & Notes:
              </div>
              <div style={{ background: 'rgba(0,0,0,0.3)', padding: '1rem', borderRadius: '8px', fontSize: '0.88rem', color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>
                {voiceResult.display_card?.body}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
