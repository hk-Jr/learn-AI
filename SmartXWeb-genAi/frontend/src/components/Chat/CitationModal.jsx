import React, { useState } from 'react';
import { X, FileText, BookOpen, Percent, Layers, Copy, Check } from 'lucide-react';

export function CitationModal({ citation, onClose }) {
  const [copied, setCopied] = useState(false);

  if (!citation) return null;

  const handleCopy = () => {
    navigator.clipboard.writeText(citation.content_snippet);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const scorePct = Math.round(citation.similarity_score * 100);

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="p-4 border-bottom d-flex align-items-center justify-content-between bg-white">
          <div className="d-flex align-items-center gap-2.5">
            <div className="p-2 rounded text-primary" style={{ backgroundColor: '#eff6ff' }}>
              <FileText size={18} />
            </div>
            <div>
              <h5 className="mb-0 fw-bold text-dark text-truncate" style={{ fontSize: '15px', maxWidth: '450px' }}>
                {citation.document_name}
              </h5>
              <div className="text-muted" style={{ fontSize: '11.5px', marginTop: '2px' }}>
                Verifiable Grounded Source Citation
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="btn btn-light btn-sm p-1.5 rounded-circle text-muted"
            style={{ width: '30px', height: '30px' }}
          >
            <X size={16} />
          </button>
        </div>

        {/* Badges Bar */}
        <div className="px-4 py-2 border-bottom d-flex flex-wrap gap-2" style={{ backgroundColor: '#fafbfc' }}>
          <span
            className="badge rounded-pill fw-medium d-flex align-items-center gap-1"
            style={{ backgroundColor: '#eff6ff', color: '#1d4ed8', border: '1px solid #bfdbfe', fontSize: '11.5px' }}
          >
            <BookOpen size={12} />
            <span>Page {citation.page_number}</span>
          </span>

          <span
            className="badge rounded-pill fw-medium d-flex align-items-center gap-1"
            style={{ backgroundColor: '#f5f3ff', color: '#6d28d9', border: '1px solid #ddd6fe', fontSize: '11.5px' }}
          >
            <Layers size={12} />
            <span>Chunk #{citation.chunk_index}</span>
          </span>

          <span
            className="badge rounded-pill fw-medium d-flex align-items-center gap-1"
            style={{ backgroundColor: '#ecfdf5', color: '#047857', border: '1px solid #a7f3d0', fontSize: '11.5px' }}
          >
            <Percent size={12} />
            <span>{scorePct}% Semantic Relevance</span>
          </span>
        </div>

        {/* Content Snippet */}
        <div className="p-4 bg-white" style={{ flex: 1, overflowY: 'auto' }}>
          <div className="d-flex align-items-center justify-content-between mb-2">
            <span className="text-muted fw-bold text-uppercase" style={{ fontSize: '11px', letterSpacing: '0.05em' }}>
              Extracted Source Text
            </span>
            <button
              onClick={handleCopy}
              className="btn btn-link btn-sm p-0 text-primary text-decoration-none d-flex align-items-center gap-1"
              style={{ fontSize: '12px' }}
            >
              {copied ? <Check size={13} className="text-success" /> : <Copy size={13} />}
              <span>{copied ? 'Copied' : 'Copy Excerpt'}</span>
            </button>
          </div>
          <div
            className="p-3 rounded-3"
            style={{
              backgroundColor: '#fafbfc',
              border: '1px solid #eaecf0',
              fontSize: '12.5px',
              lineHeight: '1.6',
              whiteSpace: 'pre-wrap',
              fontFamily: 'monospace'
            }}
          >
            {citation.content_snippet}
          </div>
        </div>

        {/* Footer */}
        <div className="p-3 border-top d-flex justify-content-end bg-white">
          <button
            onClick={onClose}
            className="btn btn-primary btn-sm px-4 fw-semibold"
            style={{ borderRadius: '8px', fontSize: '12.5px' }}
          >
            Done
          </button>
        </div>
      </div>
    </div>
  );
}

