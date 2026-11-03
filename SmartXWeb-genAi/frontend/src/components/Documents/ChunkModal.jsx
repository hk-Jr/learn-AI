import React from 'react';
import { X, Layers, Hash, BookOpen } from 'lucide-react';

export function ChunkModal({ document, onClose }) {
  if (!document) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="p-4 border-bottom d-flex align-items-center justify-content-between bg-white">
          <div className="d-flex align-items-center gap-2.5">
            <div className="p-2 rounded text-primary" style={{ backgroundColor: '#eff6ff' }}>
              <Layers size={18} />
            </div>
            <div>
              <h5 className="mb-0 fw-bold text-dark text-truncate" style={{ fontSize: '15px', maxWidth: '450px' }}>
                {document.original_name}
              </h5>
              <div className="text-muted" style={{ fontSize: '11.5px', marginTop: '2px' }}>
                Indexed Chunks ({document.chunks?.length || document.total_chunks || 0}) • {document.total_pages} Pages • {(document.file_size / 1024).toFixed(1)} KB
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

        {/* Chunks List Body */}
        <div className="p-4 overflow-y-auto d-flex flex-column gap-3" style={{ flex: 1, backgroundColor: '#ffffff' }}>
          {(!document.chunks || document.chunks.length === 0) ? (
            <div className="py-5 text-center text-muted" style={{ fontSize: '13px' }}>
              No chunks available for this document.
            </div>
          ) : (
            document.chunks.map((chunk) => (
              <div
                key={chunk.id}
                className="p-3 rounded-3"
                style={{ backgroundColor: '#fafbfc', border: '1px solid #eaecf0' }}
              >
                <div className="d-flex align-items-center justify-content-between mb-2 text-muted" style={{ fontSize: '11px', fontFamily: 'monospace' }}>
                  <span className="fw-bold text-primary d-flex align-items-center gap-1">
                    <Hash size={13} />
                    <span>Chunk #{chunk.chunk_index}</span>
                  </span>
                  <div className="d-flex align-items-center gap-3">
                    <span className="d-flex align-items-center gap-1">
                      <BookOpen size={13} />
                      <span>Page {chunk.page_number}</span>
                    </span>
                    <span>~{chunk.token_count} tokens</span>
                  </div>
                </div>
                <div
                  className="text-dark"
                  style={{
                    fontSize: '12px',
                    lineHeight: '1.6',
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'inherit'
                  }}
                >
                  {chunk.content}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Footer */}
        <div className="p-3 border-top d-flex justify-content-end bg-white">
          <button
            onClick={onClose}
            className="btn btn-primary btn-sm px-4 fw-semibold"
            style={{ borderRadius: '8px', fontSize: '12.5px' }}
          >
            Close Inspector
          </button>
        </div>
      </div>
    </div>
  );
}

