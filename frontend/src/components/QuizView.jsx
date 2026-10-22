import React, { useState } from 'react';
import { generateQuiz, submitQuiz } from '../api';

export default function QuizView({ onQuizCompleted }) {
  const [topic, setTopic] = useState('Process Synchronization');
  const [numQuestions, setNumQuestions] = useState(3);
  const [quizData, setQuizData] = useState(null);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [loading, setLoading] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const topicsList = [
    'Process Synchronization',
    'Artificial Neural Networks',
    'Convolutional Neural Networks',
    'Database Management Systems',
  ];

  const handleGenerate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setSelectedAnswers({});
    try {
      const data = await generateQuiz(topic, numQuestions);
      setQuizData(data);
    } catch (err) {
      setError(err.message || 'Failed to generate quiz');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectOption = (questionId, optKey) => {
    if (result) return; // Prevent changing after submission
    setSelectedAnswers({
      ...selectedAnswers,
      [String(questionId)]: optKey,
    });
  };

  const handleSubmit = async () => {
    if (!quizData) return;
    setSubmitting(true);
    setError(null);
    try {
      const res = await submitQuiz(quizData.quiz_id, selectedAnswers);
      setResult(res);
      if (onQuizCompleted) onQuizCompleted();
    } catch (err) {
      setError(err.message || 'Failed to submit quiz');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <span>📝</span>
          <span>Adaptive Concept Quiz & Mastery Assessment</span>
        </div>
        <p className="card-subtitle">
          Quizzes are generated directly from your uploaded engineering notes. Results update your stored topic mastery and detect specific misconceptions.
        </p>

        {/* Quiz Config Bar */}
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', marginBottom: '1.5rem', background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px' }}>
          <div>
            <label style={{ fontSize: '0.82rem', color: '#9ca3af', display: 'block', marginBottom: '0.3rem' }}>
              Select Topic:
            </label>
            <select
              className="input-field"
              style={{ width: 'auto', minWidth: '220px' }}
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              disabled={loading}
            >
              {topicsList.map((t) => (
                <option key={t} value={t} style={{ background: '#111827' }}>
                  {t}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ fontSize: '0.82rem', color: '#9ca3af', display: 'block', marginBottom: '0.3rem' }}>
              Questions:
            </label>
            <select
              className="input-field"
              style={{ width: 'auto' }}
              value={numQuestions}
              onChange={(e) => setNumQuestions(Number(e.target.value))}
              disabled={loading}
            >
              <option value={2} style={{ background: '#111827' }}>2 Questions (Quick)</option>
              <option value={3} style={{ background: '#111827' }}>3 Questions (Standard)</option>
              <option value={5} style={{ background: '#111827' }}>5 Questions (Deep Drill)</option>
            </select>
          </div>

          <div style={{ alignSelf: 'flex-end' }}>
            <button
              className="btn-primary"
              onClick={handleGenerate}
              disabled={loading}
            >
              {loading ? 'Generating from Notes...' : 'Generate Adaptive Quiz'}
            </button>
          </div>
        </div>

        {error && (
          <div className="banner" style={{ borderColor: 'rgba(244,63,94,0.4)', background: 'rgba(244,63,94,0.1)', color: '#fb7185' }}>
            <span>⚠️</span>
            <span>{error}</span>
          </div>
        )}

        {/* Quiz Questions */}
        {quizData && (
          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.75rem' }}>
              <div>
                <h3 style={{ color: '#fff', fontSize: '1.1rem' }}>{quizData.title}</h3>
                <span style={{ fontSize: '0.8rem', color: '#06b6d4' }}>
                  Source: {quizData.source_document} (Page {quizData.page})
                </span>
              </div>
              <span className="badge-proficient">{quizData.questions.length} Questions</span>
            </div>

            {quizData.questions.map((q, qIndex) => {
              const qIdStr = String(q.id);
              const studentChoice = selectedAnswers[qIdStr];
              const feedbackItem = result?.feedback?.find((f) => String(f.question_id) === qIdStr);

              return (
                <div
                  key={q.id}
                  style={{
                    background: 'rgba(255, 255, 255, 0.02)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '10px',
                    padding: '1.25rem',
                    marginBottom: '1.25rem'
                  }}
                >
                  <div style={{ fontWeight: 600, fontSize: '0.95rem', marginBottom: '0.85rem', color: '#f3f4f6' }}>
                    <span style={{ color: '#06b6d4', marginRight: '6px' }}>Q{qIndex + 1}.</span>
                    {q.question}
                  </div>

                  <div>
                    {Object.entries(q.options || {}).map(([optKey, optText]) => {
                      const isSelected = studentChoice === optKey;
                      let optionStyle = {};

                      if (result && feedbackItem) {
                        if (optKey === feedbackItem.correct_answer) {
                          optionStyle = { borderColor: '#10b981', background: 'rgba(16,185,129,0.15)' };
                        } else if (isSelected && !feedbackItem.is_correct) {
                          optionStyle = { borderColor: '#f43f5e', background: 'rgba(244,63,94,0.15)' };
                        }
                      }

                      return (
                        <div
                          key={optKey}
                          className={`quiz-option ${isSelected ? 'selected' : ''}`}
                          style={optionStyle}
                          onClick={() => handleSelectOption(q.id, optKey)}
                        >
                          <span className="option-badge">{optKey}</span>
                          <span style={{ fontSize: '0.9rem', color: '#e5e7eb' }}>{optText}</span>
                        </div>
                      );
                    })}
                  </div>

                  {feedbackItem && (
                    <div style={{ marginTop: '0.85rem', padding: '0.75rem', borderRadius: '6px', background: feedbackItem.is_correct ? 'rgba(16,185,129,0.1)' : 'rgba(244,63,94,0.1)', borderLeft: `3px solid ${feedbackItem.is_correct ? '#10b981' : '#f43f5e'}` }}>
                      <div style={{ fontWeight: 600, fontSize: '0.82rem', color: feedbackItem.is_correct ? '#34d399' : '#fb7185', marginBottom: '0.25rem' }}>
                        {feedbackItem.is_correct ? '✅ Correct!' : '❌ Concept Review Needed:'}
                      </div>
                      <div style={{ fontSize: '0.84rem', color: '#d1d5db' }}>
                        {feedbackItem.explanation}
                      </div>
                    </div>
                  )}
                </div>
              );
            })}

            {!result ? (
              <div style={{ textAlign: 'right', marginTop: '1rem' }}>
                <button
                  className="btn-primary"
                  onClick={handleSubmit}
                  disabled={submitting || Object.keys(selectedAnswers).length === 0}
                >
                  {submitting ? 'Evaluating Answers...' : 'Submit Answers & Update Mastery'}
                </button>
              </div>
            ) : (
              <div style={{ background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.3)', borderRadius: '12px', padding: '1.25rem', marginTop: '1.5rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
                  <div>
                    <h4 style={{ fontSize: '1.1rem', color: '#fff' }}>Assessment Summary</h4>
                    <span style={{ fontSize: '0.85rem', color: '#9ca3af' }}>
                      Topic: {result.topic} • Status: <span className={result.status === 'Mastered' ? 'badge-mastered' : (result.status === 'Proficient' ? 'badge-proficient' : 'badge-review')}>{result.status}</span>
                    </span>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.8rem', fontWeight: 700, color: result.score >= 70 ? '#34d399' : '#fb7185' }}>
                      {result.score}%
                    </div>
                    <span style={{ fontSize: '0.8rem', color: '#9ca3af' }}>
                      {result.correct_count} / {result.total_questions} Correct
                    </span>
                  </div>
                </div>

                {result.detected_misconceptions && result.detected_misconceptions.length > 0 && (
                  <div style={{ marginTop: '0.85rem', padding: '0.75rem', background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.25)', borderRadius: '8px' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.82rem', color: '#fb7185', marginBottom: '0.4rem' }}>
                      ⚠️ Detected Misconceptions:
                    </div>
                    {result.detected_misconceptions.map((m, mIdx) => (
                      <div key={mIdx} style={{ fontSize: '0.8rem', color: '#f3f4f6', marginBottom: '0.3rem' }}>
                        • <strong>{m.concept}</strong>: {m.remediation}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
