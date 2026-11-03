import React, { useState } from 'react';
import {
  UploadCloud,
  FileText,
  Search,
  RefreshCw,
  Trash2,
  Eye,
  CheckCircle2,
  Clock,
  AlertCircle
} from 'lucide-react';
import { api } from '../../api/client';
import { ChunkModal } from './ChunkModal';

export function DocumentsView({ documents, loading, onRefresh }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);
  const [actionInProgress, setActionInProgress] = useState(null);

  const handleFileUpload = async (files) => {
    if (!files || files.length === 0) return;
    setUploading(true);
    setUploadError(null);
    try {
      await api.uploadDocuments(Array.from(files));
      onRefresh();
    } catch (err) {
      setUploadError(err.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"? This removes all vector embeddings and chunks permanently.`)) {
      return;
    }
    setActionInProgress(id);
    try {
      await api.deleteDocument(id);
      onRefresh();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleReprocess = async (id) => {
    setActionInProgress(id);
    try {
      await api.reprocessDocument(id);
      onRefresh();
    } catch (err) {
      alert(`Reprocessing failed: ${err.message}`);
    } finally {
      setActionInProgress(null);
    }
  };

  const handleViewChunks = async (doc) => {
    try {
      const detailed = await api.getDocument(doc.id);
      setSelectedDoc(detailed);
    } catch {
      setSelectedDoc(doc);
    }
  };

  const filteredDocs = documents.filter((doc) => {
    const matchesSearch = doc.original_name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || doc.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  return (
    <div className="container-fluid p-0" style={{ maxWidth: '1200px' }}>
      {/* Upload Dropzone */}
      <div className="app-card p-4 mb-4">
        <label
          className="w-100 d-flex flex-column align-items-center justify-content-center p-5 rounded-3 text-center cursor-pointer"
          style={{
            border: '2px dashed #d1d5db',
            backgroundColor: '#fafbfc',
            cursor: 'pointer',
            transition: 'border-color 0.2s ease'
          }}
        >
          <UploadCloud size={40} className="text-primary mb-2" />
          <div className="fw-bold text-dark" style={{ fontSize: '14px' }}>
            {uploading ? 'Processing & Indexing Document Vectors...' : 'Click to upload or drag & drop documents'}
          </div>
          <div className="text-muted mt-1" style={{ fontSize: '12px' }}>
            Supports PDF, DOCX, TXT, and Markdown files (up to 50MB)
          </div>
          <input
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.md"
            onChange={(e) => handleFileUpload(e.target.files)}
            disabled={uploading}
            className="d-none"
          />
        </label>
        {uploadError && (
          <div className="mt-2 text-danger d-flex align-items-center gap-1.5" style={{ fontSize: '12px' }}>
            <AlertCircle size={14} />
            <span>{uploadError}</span>
          </div>
        )}
      </div>

      {/* Search and Filters */}
      <div className="d-flex flex-column flex-sm-row align-items-center justify-content-between gap-3 mb-3">
        <div className="position-relative w-100" style={{ maxWidth: '340px' }}>
          <Search size={15} className="position-absolute text-muted" style={{ left: '12px', top: '50%', transform: 'translateY(-50%)' }} />
          <input
            type="text"
            placeholder="Search documents by name..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="form-control form-control-sm ps-5 rounded-pill"
            style={{ fontSize: '12.5px', borderColor: '#eaecf0', height: '36px' }}
          />
        </div>

        <div className="d-flex align-items-center gap-2">
          <div className="d-flex p-1 rounded-pill" style={{ backgroundColor: '#f2f4f7' }}>
            {['all', 'indexed', 'processing', 'error'].map((s) => (
              <button
                key={s}
                onClick={() => setStatusFilter(s)}
                className={`btn btn-sm text-capitalize rounded-pill px-3 py-1 fw-medium ${
                  statusFilter === s ? 'btn-white bg-white text-primary shadow-sm' : 'text-secondary'
                }`}
                style={{ fontSize: '12px', border: 'none' }}
              >
                {s}
              </button>
            ))}
          </div>

          <button
            onClick={onRefresh}
            className="btn btn-outline-secondary btn-sm p-2 rounded-circle"
            title="Refresh document status"
            style={{ width: '36px', height: '36px', borderColor: '#eaecf0' }}
          >
            <RefreshCw size={14} className={loading ? 'spinner-border spinner-border-sm' : ''} />
          </button>
        </div>
      </div>

      {/* Documents Table */}
      <div className="app-card p-0 overflow-hidden">
        {filteredDocs.length === 0 ? (
          <div className="py-5 text-center text-muted" style={{ fontSize: '13px' }}>
            <FileText size={36} className="text-muted opacity-50 mb-2" />
            <div>{searchTerm ? 'No documents match your search query.' : 'No documents indexed in knowledge base yet.'}</div>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="plane-table mb-0">
              <thead>
                <tr>
                  <th>Document</th>
                  <th>Size</th>
                  <th>Pages</th>
                  <th>Chunks</th>
                  <th>Status</th>
                  <th>Uploaded</th>
                  <th className="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredDocs.map((doc) => (
                  <tr key={doc.id}>
                    <td>
                      <div className="d-flex align-items-center gap-2.5">
                        <div
                          className="d-flex align-items-center justify-content-center fw-bold text-uppercase rounded"
                          style={{
                            width: '32px',
                            height: '32px',
                            backgroundColor: '#eff6ff',
                            color: '#2563eb',
                            fontSize: '10px'
                          }}
                        >
                          {doc.file_type.replace('.', '')}
                        </div>
                        <div className="text-truncate" style={{ maxWidth: '320px' }}>
                          <div className="fw-semibold text-dark text-truncate">{doc.original_name}</div>
                          {doc.error_message && (
                            <div className="text-danger text-truncate" style={{ fontSize: '10.5px' }} title={doc.error_message}>
                              {doc.error_message}
                            </div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="text-secondary">{(doc.file_size / 1024).toFixed(1)} KB</td>
                    <td className="text-secondary">{doc.total_pages}</td>
                    <td>
                      <span className="fw-bold font-monospace text-primary">{doc.total_chunks}</span>
                    </td>
                    <td>
                      <span
                        className="badge rounded-pill fw-semibold text-capitalize"
                        style={{
                          fontSize: '11px',
                          backgroundColor: doc.status === 'indexed' ? '#ecfdf5' : doc.status === 'processing' ? '#fffbeb' : '#fef2f2',
                          color: doc.status === 'indexed' ? '#047857' : doc.status === 'processing' ? '#b45309' : '#b91c1c',
                          border: `1px solid ${doc.status === 'indexed' ? '#a7f3d0' : doc.status === 'processing' ? '#fde68a' : '#fecaca'}`
                        }}
                      >
                        {doc.status === 'indexed' && <CheckCircle2 size={11} className="me-1" />}
                        {doc.status === 'processing' && <Clock size={11} className="me-1" />}
                        {doc.status === 'error' && <AlertCircle size={11} className="me-1" />}
                        {doc.status}
                      </span>
                    </td>
                    <td className="text-muted" style={{ fontSize: '12px' }}>
                      {new Date(doc.uploaded_at).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
                    </td>
                    <td className="text-end">
                      <div className="d-inline-flex gap-1">
                        <button
                          onClick={() => handleViewChunks(doc)}
                          className="btn btn-light btn-sm p-1.5 rounded text-secondary"
                          title="Inspect chunks"
                        >
                          <Eye size={14} />
                        </button>
                        <button
                          onClick={() => handleReprocess(doc.id)}
                          disabled={actionInProgress === doc.id}
                          className="btn btn-light btn-sm p-1.5 rounded text-secondary"
                          title="Reprocess document"
                        >
                          <RefreshCw size={14} className={actionInProgress === doc.id ? 'spinner-border spinner-border-sm' : ''} />
                        </button>
                        <button
                          onClick={() => handleDelete(doc.id, doc.original_name)}
                          disabled={actionInProgress === doc.id}
                          className="btn btn-light btn-sm p-1.5 rounded text-danger"
                          title="Delete document"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Chunk Modal */}
      <ChunkModal
        document={selectedDoc}
        onClose={() => setSelectedDoc(null)}
      />
    </div>
  );
}

