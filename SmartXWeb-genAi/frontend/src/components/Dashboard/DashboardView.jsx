import React, { useState } from 'react';
import {
  FileText,
  CheckCircle2,
  Clock,
  AlertCircle,
  MessageSquare,
  Layers,
  UploadCloud,
  ArrowRight,
  Sparkles,
  Zap
} from 'lucide-react';
import { api } from '../../api/client';

export function DashboardView({ stats, loading, onNavigate, onUploadSuccess }) {
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const handleFileChange = async (e) => {
    if (!e.target.files || e.target.files.length === 0) return;
    setUploading(true);
    setUploadError(null);
    try {
      await api.uploadDocuments(Array.from(e.target.files));
      onUploadSuccess();
    } catch (err) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  if (loading || !stats) {
    return (
      <div className="d-flex align-items-center justify-content-center h-100 p-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid p-0" style={{ maxWidth: '1200px' }}>
      {/* Welcome Banner */}
      <div
        className="p-4 mb-4 rounded-4 text-white d-flex flex-column justify-content-between"
        style={{
          background: 'linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #3b82f6 100%)',
          boxShadow: '0 4px 12px rgba(37, 99, 235, 0.15)'
        }}
      >
        <div style={{ maxWidth: '650px' }}>
          <div className="d-inline-flex align-items-center gap-1.5 px-2.5 py-1 rounded-pill bg-white bg-opacity-25 text-white mb-2" style={{ fontSize: '11px', fontWeight: '600' }}>
            <Sparkles size={13} />
            <span>AI Knowledge Engine Active</span>
          </div>
          <h2 className="fw-bold mb-2" style={{ fontSize: '24px' }}>
            Intelligent Document Retrieval & Question Answering
          </h2>
          <p className="text-white text-opacity-75 mb-3" style={{ fontSize: '13px', lineHeight: '1.5' }}>
            Upload PDF, DOCX, and TXT files to build your semantic knowledge base. Ask questions grounded in your private enterprise documentation with exact source citations.
          </p>
          <div className="d-flex gap-2">
            <button
              onClick={() => onNavigate('chat')}
              className="btn btn-light btn-sm fw-semibold d-flex align-items-center gap-1.5 px-3 py-2 text-primary"
              style={{ borderRadius: '8px', fontSize: '12.5px' }}
            >
              <span>Ask a Question</span>
              <ArrowRight size={14} />
            </button>
            <button
              onClick={() => onNavigate('documents')}
              className="btn btn-outline-light btn-sm fw-semibold px-3 py-2"
              style={{ borderRadius: '8px', fontSize: '12.5px' }}
            >
              <span>Manage Documents</span>
            </button>
          </div>
        </div>
      </div>

      {/* Metric Cards */}
      <div className="row g-3 mb-4">
        {/* Total Documents */}
        <div className="col-12 col-sm-6 col-lg-3">
          <div className="app-card h-100 p-3">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted fw-semibold text-uppercase" style={{ fontSize: '11px' }}>Total Documents</span>
              <div className="p-2 rounded" style={{ backgroundColor: '#eff6ff', color: '#2563eb' }}>
                <FileText size={18} />
              </div>
            </div>
            <div className="d-flex align-items-baseline justify-content-between mt-2">
              <span className="fw-bold fs-3 text-dark">{stats.total_documents}</span>
              <span className="text-success fw-semibold d-flex align-items-center gap-1" style={{ fontSize: '11px' }}>
                <CheckCircle2 size={13} />
                {stats.processed_documents} Indexed
              </span>
            </div>
          </div>
        </div>

        {/* Total Chunks */}
        <div className="col-12 col-sm-6 col-lg-3">
          <div className="app-card h-100 p-3">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted fw-semibold text-uppercase" style={{ fontSize: '11px' }}>Vector Chunks</span>
              <div className="p-2 rounded" style={{ backgroundColor: '#f5f3ff', color: '#7c3aed' }}>
                <Layers size={18} />
              </div>
            </div>
            <div className="d-flex align-items-baseline justify-content-between mt-2">
              <span className="fw-bold fs-3 text-dark">{stats.total_chunks}</span>
              <span className="text-muted" style={{ fontSize: '11.5px' }}>In ChromaDB</span>
            </div>
          </div>
        </div>

        {/* Questions Asked */}
        <div className="col-12 col-sm-6 col-lg-3">
          <div className="app-card h-100 p-3">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted fw-semibold text-uppercase" style={{ fontSize: '11px' }}>Questions Asked</span>
              <div className="p-2 rounded" style={{ backgroundColor: '#ecfdf5', color: '#059669' }}>
                <MessageSquare size={18} />
              </div>
            </div>
            <div className="d-flex align-items-baseline justify-content-between mt-2">
              <span className="fw-bold fs-3 text-dark">{stats.total_questions_asked}</span>
              <span className="text-muted" style={{ fontSize: '11.5px' }}>{stats.total_conversations} Sessions</span>
            </div>
          </div>
        </div>

        {/* Pipeline Health */}
        <div className="col-12 col-sm-6 col-lg-3">
          <div className="app-card h-100 p-3">
            <div className="d-flex align-items-center justify-content-between mb-2">
              <span className="text-muted fw-semibold text-uppercase" style={{ fontSize: '11px' }}>Pipeline Status</span>
              <div className="p-2 rounded" style={{ backgroundColor: '#fffbeb', color: '#d97706' }}>
                <Zap size={18} />
              </div>
            </div>
            <div className="d-flex align-items-baseline justify-content-between mt-2">
              <span className="fw-bold text-success" style={{ fontSize: '18px' }}>100% Operational</span>
              <span className="text-muted" style={{ fontSize: '11.5px' }}>Live Indexing</span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid: Recent Documents & Quick Upload */}
      <div className="row g-4">
        {/* Recent Documents */}
        <div className="col-12 col-lg-8">
          <div className="app-card p-4">
            <div className="d-flex align-items-center justify-content-between mb-3">
              <div>
                <h3 className="h6 fw-bold mb-0 text-dark">Recent Documents</h3>
                <p className="text-muted mb-0" style={{ fontSize: '12px' }}>Latest files indexed into ChromaDB knowledge base</p>
              </div>
              <button
                onClick={() => onNavigate('documents')}
                className="btn btn-link text-primary p-0 d-flex align-items-center gap-1 text-decoration-none fw-semibold"
                style={{ fontSize: '12.5px' }}
              >
                <span>View All</span>
                <ArrowRight size={13} />
              </button>
            </div>

            {stats.recent_documents.length === 0 ? (
              <div className="py-5 text-center text-muted" style={{ fontSize: '13px' }}>
                No documents uploaded yet.
              </div>
            ) : (
              <div className="list-group list-group-flush">
                {stats.recent_documents.map((doc) => (
                  <div key={doc.id} className="list-group-item d-flex align-items-center justify-content-between px-2 py-3 border-bottom">
                    <div className="d-flex align-items-center gap-2.5 text-truncate">
                      <div
                        className="d-flex align-items-center justify-content-center fw-bold text-uppercase rounded"
                        style={{
                          width: '34px',
                          height: '34px',
                          backgroundColor: '#eff6ff',
                          color: '#2563eb',
                          fontSize: '10px'
                        }}
                      >
                        {doc.file_type.replace('.', '')}
                      </div>
                      <div className="text-truncate">
                        <div className="fw-semibold text-dark text-truncate" style={{ fontSize: '13px' }}>{doc.original_name}</div>
                        <div className="text-muted" style={{ fontSize: '11.5px' }}>
                          {(doc.file_size / 1024).toFixed(1)} KB • {doc.total_pages} {doc.total_pages === 1 ? 'page' : 'pages'} • {doc.total_chunks} chunks
                        </div>
                      </div>
                    </div>
                    <span
                      className="badge rounded-pill fw-semibold text-capitalize"
                      style={{
                        fontSize: '11px',
                        backgroundColor: doc.status === 'indexed' ? '#ecfdf5' : doc.status === 'processing' ? '#fffbeb' : '#fef2f2',
                        color: doc.status === 'indexed' ? '#047857' : doc.status === 'processing' ? '#b45309' : '#b91c1c',
                        border: `1px solid ${doc.status === 'indexed' ? '#a7f3d0' : doc.status === 'processing' ? '#fde68a' : '#fecaca'}`
                      }}
                    >
                      {doc.status}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Quick Ingestion & Activity */}
        <div className="col-12 col-lg-4 d-flex flex-column gap-4">
          {/* Upload Dropzone */}
          <div className="app-card p-4">
            <h3 className="h6 fw-bold mb-1 text-dark">Quick Ingestion</h3>
            <p className="text-muted mb-3" style={{ fontSize: '12px' }}>Upload files for automated chunking & vector indexing</p>

            <label
              className="w-100 d-flex flex-column align-items-center justify-content-center p-4 rounded-3 text-center cursor-pointer"
              style={{
                border: '2px dashed #d1d5db',
                backgroundColor: '#fafbfc',
                cursor: 'pointer',
                transition: 'all 0.15s ease'
              }}
            >
              <UploadCloud size={32} className="text-primary mb-2" />
              <span className="fw-semibold text-dark" style={{ fontSize: '12.5px' }}>
                {uploading ? 'Processing & Indexing...' : 'Upload PDF, DOCX, TXT'}
              </span>
              <span className="text-muted mt-1" style={{ fontSize: '11px' }}>Multiple file upload supported</span>
              <input
                type="file"
                multiple
                accept=".pdf,.docx,.txt,.md"
                onChange={handleFileChange}
                disabled={uploading}
                className="d-none"
              />
            </label>
            {uploadError && (
              <div className="mt-2 text-danger d-flex align-items-center gap-1" style={{ fontSize: '11.5px' }}>
                <AlertCircle size={13} />
                <span>{uploadError}</span>
              </div>
            )}
          </div>

          {/* Activity Stream */}
          <div className="app-card p-4">
            <h3 className="h6 fw-bold mb-2 text-dark">Recent Activity</h3>
            {stats.recent_activity.length === 0 ? (
              <div className="text-muted" style={{ fontSize: '12px' }}>No activity logged yet.</div>
            ) : (
              <div className="d-flex flex-column gap-2.5">
                {stats.recent_activity.slice(0, 5).map((act) => (
                  <div key={act.id} className="d-flex align-items-start gap-2" style={{ fontSize: '12px' }}>
                    <div className="p-1 rounded bg-light text-secondary mt-0.5">
                      {act.type === 'document_upload' ? <FileText size={12} /> : <MessageSquare size={12} />}
                    </div>
                    <div className="text-truncate flex-grow-1">
                      <div className="fw-medium text-dark text-truncate">{act.title}</div>
                      <div className="text-muted" style={{ fontSize: '10.5px' }}>
                        {new Date(act.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

