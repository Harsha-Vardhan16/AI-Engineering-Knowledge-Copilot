import React, { useState, useEffect } from 'react';
import { listDocuments, uploadDocument, ingestSampleDocuments } from '../api';

export default function DocumentsView({ onDocumentsUpdated }) {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [ingesting, setIngesting] = useState(false);
  const [statusMsg, setStatusMsg] = useState(null);

  const fetchDocs = async () => {
    setLoading(true);
    try {
      const data = await listDocuments();
      setDocs(data.documents || []);
    } catch (err) {
      console.error("Failed to list documents:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocs();
  }, []);

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setStatusMsg(null);
    try {
      const res = await uploadDocument(file);
      if (res.success) {
        setStatusMsg({ type: 'success', text: res.message });
      } else {
        setStatusMsg({ type: 'error', text: res.message });
      }
      fetchDocs();
      if (onDocumentsUpdated) onDocumentsUpdated();
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message });
    } finally {
      setUploading(false);
      e.target.value = '';
    }
  };

  const handleIngestSamples = async () => {
    setIngesting(true);
    setStatusMsg(null);
    try {
      const res = await ingestSampleDocuments();
      setStatusMsg({ type: 'success', text: res.message });
      fetchDocs();
      if (onDocumentsUpdated) onDocumentsUpdated();
    } catch (err) {
      setStatusMsg({ type: 'error', text: err.message });
    } finally {
      setIngesting(false);
    }
  };

  return (
    <div>
      <div className="card">
        <div className="card-title">
          <span>📚</span>
          <span>RAG Course Notes Repository</span>
        </div>
        <p className="card-subtitle">
          Uploaded engineering notes are extracted, chunked, embedded, and indexed with exact page-level citations in FAISS and SQLite.
        </p>

        {/* Upload & Ingestion Actions */}
        <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', marginBottom: '1.5rem', background: 'rgba(255,255,255,0.02)', padding: '1.25rem', borderRadius: '8px' }}>
          <div>
            <label className="btn-primary" style={{ cursor: 'pointer', margin: 0 }}>
              <span>📤</span>
              <span>{uploading ? 'Processing & Indexing...' : 'Upload Engineering PDF'}</span>
              <input
                type="file"
                accept=".pdf"
                style={{ display: 'none' }}
                onChange={handleFileUpload}
                disabled={uploading || ingesting}
              />
            </label>
          </div>

          <div>
            <button
              className="btn-secondary"
              onClick={handleIngestSamples}
              disabled={uploading || ingesting}
            >
              <span>⚡</span>
              <span>{ingesting ? 'Indexing Sample PDFs...' : 'Re-index Sample Course Notes'}</span>
            </button>
          </div>

          <div style={{ fontSize: '0.82rem', color: '#9ca3af' }}>
            Supports multi-page syllabus PDFs, lecture slides, and engineering textbooks.
          </div>
        </div>

        {statusMsg && (
          <div
            className="banner"
            style={{
              borderColor: statusMsg.type === 'success' ? 'rgba(16,185,129,0.4)' : 'rgba(244,63,94,0.4)',
              background: statusMsg.type === 'success' ? 'rgba(16,185,129,0.1)' : 'rgba(244,63,94,0.1)',
              color: statusMsg.type === 'success' ? '#34d399' : '#fb7185'
            }}
          >
            <span>{statusMsg.type === 'success' ? '✅' : '⚠️'}</span>
            <span>{statusMsg.text}</span>
          </div>
        )}

        {/* Documents Table */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#9ca3af' }}>
            Loading course notes...
          </div>
        ) : docs.length > 0 ? (
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.88rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)', color: '#9ca3af' }}>
                  <th style={{ padding: '0.75rem' }}>Document</th>
                  <th style={{ padding: '0.75rem' }}>Topic Domain</th>
                  <th style={{ padding: '0.75rem' }}>Pages</th>
                  <th style={{ padding: '0.75rem' }}>Chunks</th>
                  <th style={{ padding: '0.75rem' }}>Status</th>
                </tr>
              </thead>
              <tbody>
                {docs.map((d) => (
                  <tr key={d.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                    <td style={{ padding: '0.75rem', fontWeight: 600, color: '#f3f4f6' }}>
                      📄 {d.filename}
                    </td>
                    <td style={{ padding: '0.75rem' }}>
                      <span className="tool-pill" style={{ background: 'rgba(6,182,212,0.1)', borderColor: 'rgba(6,182,212,0.3)', color: '#06b6d4' }}>
                        {d.topic}
                      </span>
                    </td>
                    <td style={{ padding: '0.75rem', color: '#cbd5e1' }}>
                      {d.pages} pages
                    </td>
                    <td style={{ padding: '0.75rem', color: '#cbd5e1' }}>
                      {d.chunks_count} chunks
                    </td>
                    <td style={{ padding: '0.75rem' }}>
                      <span className="badge-mastered">Indexed & Searchable</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div style={{ textAlign: 'center', padding: '2rem', color: '#9ca3af', background: 'rgba(255,255,255,0.02)', borderRadius: '8px' }}>
            No documents indexed yet. Click <strong>Re-index Sample Course Notes</strong> or upload a PDF above.
          </div>
        )}
      </div>
    </div>
  );
}
