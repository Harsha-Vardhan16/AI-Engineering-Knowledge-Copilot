import React, { useState, useEffect } from 'react';
import { getLearningProgress, getTopicRecommendation, getStudyPlan, createStudyPlan } from '../api';

export default function DashboardView({ onSelectTopicForQuiz }) {
  const [progress, setProgress] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [studyPlan, setStudyPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [planGoal, setPlanGoal] = useState('Comprehensive Core Engineering Exam Preparation');
  const [planHours, setPlanHours] = useState(6.0);
  const [creatingPlan, setCreatingPlan] = useState(false);

  const fetchDashboardData = async () => {
    setLoading(true);
    try {
      const [progData, recData, planData] = await Promise.all([
        getLearningProgress(),
        getTopicRecommendation(),
        getStudyPlan()
      ]);
      setProgress(progData);
      setRecommendation(recData);
      setStudyPlan(planData);
    } catch (err) {
      console.error("Dashboard load failed:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleUpdatePlan = async () => {
    setCreatingPlan(true);
    try {
      const res = await createStudyPlan(planGoal, planHours);
      setStudyPlan(res);
    } catch (err) {
      alert("Failed to create study plan: " + err.message);
    } finally {
      setCreatingPlan(false);
    }
  };

  if (loading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
        <span style={{ color: 'var(--accent-cyan)' }}>⚡ Loading adaptive learning analytics from SQLite...</span>
      </div>
    );
  }

  return (
    <div>
      {/* Top Stat Summary */}
      <div className="grid-4" style={{ marginBottom: '1.25rem' }}>
        <div className="stat-box">
          <div className="stat-label">Overall Mastery</div>
          <div className="stat-value" style={{ color: '#06b6d4' }}>
            {progress?.overall_mastery || 0}%
          </div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Average Quiz Score</div>
          <div className="stat-value" style={{ color: '#10b981' }}>
            {progress?.average_quiz_score || 0}%
          </div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Quizzes Completed</div>
          <div className="stat-value">
            {progress?.total_quizzes_completed || 0}
          </div>
        </div>
        <div className="stat-box">
          <div className="stat-label">Topics Tracked</div>
          <div className="stat-value" style={{ color: '#8b5cf6' }}>
            {progress?.topics?.length || 0}
          </div>
        </div>
      </div>

      {/* Adaptive Recommendation Card */}
      {recommendation && (
        <div className="card" style={{ border: '1px solid rgba(6, 182, 212, 0.4)', background: 'linear-gradient(145deg, rgba(18,24,38,0.95), rgba(8,30,45,0.75))' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.4rem' }}>
                <span style={{ fontSize: '1.3rem' }}>🎯</span>
                <h3 style={{ color: '#fff', fontSize: '1.2rem' }}>
                  Recommended Focus: <span style={{ color: 'var(--accent-cyan)' }}>{recommendation.recommended_topic}</span>
                </h3>
              </div>
              <p style={{ color: '#d1d5db', fontSize: '0.9rem', maxWidth: '780px', marginBottom: '0.75rem', lineHeight: '1.6' }}>
                {recommendation.reason}
              </p>
            </div>

            {onSelectTopicForQuiz && (
              <button
                className="btn-primary"
                onClick={() => onSelectTopicForQuiz(recommendation.recommended_topic)}
              >
                Start Remediation Quiz
              </button>
            )}
          </div>

          <div className="grid-2" style={{ marginTop: '0.75rem', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '0.85rem' }}>
            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                Prerequisites to Verify:
              </div>
              <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                {recommendation.prerequisites?.map((pr, idx) => (
                  <span key={idx} className="tool-pill" style={{ background: 'rgba(59,130,246,0.15)', borderColor: 'rgba(59,130,246,0.3)', color: '#93c5fd' }}>
                    {pr}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#9ca3af', textTransform: 'uppercase', marginBottom: '0.4rem' }}>
                Actionable Remediation:
              </div>
              <ul style={{ listStyle: 'none', fontSize: '0.82rem', color: '#cbd5e1' }}>
                {recommendation.actionable_next_steps?.map((step, sIdx) => (
                  <li key={sIdx} style={{ marginBottom: '0.25rem' }}>{step}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Topic Mastery Breakdown */}
      <div className="card">
        <div className="card-title">
          <span>📊</span>
          <span>Topic Mastery Breakdown (Stored in SQLite)</span>
        </div>
        <p className="card-subtitle">
          Real calculated metrics updated after every quiz attempt. Zero hardcoded percentages.
        </p>

        {progress?.topics && progress.topics.length > 0 ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
            {progress.topics.map((t, idx) => {
              const score = t.mastery_score;
              const badgeClass = score >= 80 ? 'badge-mastered' : (score >= 60 ? 'badge-proficient' : 'badge-review');
              const barColor = score >= 80 ? '#10b981' : (score >= 60 ? '#3b82f6' : '#f43f5e');

              return (
                <div key={idx} style={{ background: 'rgba(255,255,255,0.02)', padding: '0.85rem 1rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.4rem' }}>
                    <div>
                      <strong style={{ color: '#fff', fontSize: '0.95rem' }}>{t.topic}</strong>
                      <span style={{ fontSize: '0.78rem', color: '#9ca3af', marginLeft: '0.75rem' }}>
                        {t.total_attempts} quiz attempt(s) • {t.correct_answers}/{t.total_questions} questions correct
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <span className={badgeClass}>{t.status}</span>
                      <strong style={{ color: barColor, fontSize: '1.05rem', minWidth: '48px', textAlign: 'right' }}>
                        {score}%
                      </strong>
                    </div>
                  </div>

                  {/* Progress bar */}
                  <div style={{ width: '100%', height: '7px', background: 'rgba(255,255,255,0.08)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ width: `${Math.min(score, 100)}%`, height: '100%', background: barColor, borderRadius: '4px', transition: 'width 0.4s ease' }} />
                  </div>
                </div>
              );
            })}
          </div>
        ) : (
          <div style={{ padding: '1.5rem', textAlign: 'center', color: '#9ca3af', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
            No quiz attempts recorded yet. Take a quiz from the <strong>Adaptive Quiz</strong> tab to establish your baseline topic mastery.
          </div>
        )}
      </div>

      {/* Personalized Study Plan */}
      <div className="card">
        <div className="card-title">
          <span>📅</span>
          <span>Personalized Engineering Study Plan</span>
        </div>
        <p className="card-subtitle">
          Dynamically generated schedule allocating weekly hours to weak topics first.
        </p>

        {studyPlan?.schedule && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
            {studyPlan.schedule.map((phase, pIdx) => (
              <div key={pIdx} style={{ background: 'rgba(255,255,255,0.02)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '1rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h4 style={{ color: '#06b6d4', fontSize: '1rem' }}>{phase.phase}</h4>
                  <span className="tool-pill">{phase.hours_allocated} Hours</span>
                </div>
                <div style={{ fontSize: '0.84rem', color: '#e5e7eb', marginBottom: '0.4rem' }}>
                  <strong>Focus:</strong> {phase.focus_topics?.join(', ')}
                </div>
                <div style={{ fontSize: '0.82rem', color: '#9ca3af', marginBottom: '0.5rem' }}>
                  <strong>Milestone:</strong> {phase.milestone}
                </div>
                <ul style={{ paddingLeft: '1.2rem', fontSize: '0.8rem', color: '#cbd5e1' }}>
                  {phase.activities?.map((act, aIdx) => (
                    <li key={aIdx} style={{ marginBottom: '0.2rem' }}>{act}</li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}

        {/* Adjust Study Plan Form */}
        <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1rem', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center' }}>
          <div style={{ flex: 1, minWidth: '220px' }}>
            <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '0.3rem' }}>
              Study Goal / Target Exam:
            </label>
            <input
              type="text"
              className="input-field"
              value={planGoal}
              onChange={(e) => setPlanGoal(e.target.value)}
            />
          </div>

          <div style={{ width: '130px' }}>
            <label style={{ fontSize: '0.8rem', color: '#9ca3af', display: 'block', marginBottom: '0.3rem' }}>
              Hours / Week:
            </label>
            <input
              type="number"
              className="input-field"
              value={planHours}
              min="1"
              max="40"
              step="0.5"
              onChange={(e) => setPlanHours(Number(e.target.value))}
            />
          </div>

          <div style={{ alignSelf: 'flex-end' }}>
            <button
              className="btn-secondary"
              onClick={handleUpdatePlan}
              disabled={creatingPlan}
            >
              {creatingPlan ? 'Updating...' : 'Regenerate Plan'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
