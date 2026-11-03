import React, { useState } from 'react';
import { Search, FileText } from 'lucide-react';
import { api } from '../../api/client';
import { CitationModal } from '../Chat/CitationModal';

export function SearchView({ documents }) {
  const [query, setQuery] = useState('');
  const [topK, setTopK] = useState(5);
  const [threshold, setThreshold] = useState(0.0);
  const [selectedDocId, setSelectedDocId] = useState('all');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);
  const [inspectCitation, setInspectCitation] = useState(null);

  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setSearched(true);
    try {
      const docIds = selectedDocId === 'all' ? undefined : [selectedDocId];
      const res = await api.search({
        query: query.trim(),
        top_k: topK,
        similarity_threshold: threshold,
        document_ids: docIds,
      });
      setResults(res.results);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container-fluid p-0" style={{ maxWidth: '1000px' }}>
      {/* Search Header Card */}
      <div className="app-card p-4 mb-4">
        <h2 className="h6 fw-bold mb-1 text-dark">Semantic Similarity Explorer</h2>
        <p className="text-muted mb-3" style={{ fontSize: '12.5px' }}>
          Query your indexed ChromaDB vector store directly to inspect similarity metrics and chunk relevancy.
        </p>

        <form onSubmit={handleSearch} className="d-flex gap-2 mb-3">
          <div className="position-relative flex-grow-1">
            <Search size={15} className="position-absolute text-muted" style={{ left: '14px', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter search query or keywords to test vector retrieval..."
              className="form-control form-control-sm ps-5 rounded-pill"
              style={{ fontSize: '13px', borderColor: '#eaecf0', height: '40px' }}
            />
          </div>
          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="btn btn-primary btn-sm px-4 rounded-pill fw-semibold"
            style={{ fontSize: '12.5px' }}
          >
            {loading ? 'Searching...' : 'Explore Vectors'}
          </button>
        </form>

        {/* Sliders and filters */}
        <div className="row g-3 pt-2" style={{ fontSize: '12px' }}>
          <div className="col-12 col-md-4">
            <div className="d-flex justify-content-between text-muted mb-1">
              <span>Top-K Results</span>
              <span className="fw-bold text-dark">{topK}</span>
            </div>
            <input
              type="range"
              min="1"
              max="15"
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              className="form-range"
            />
          </div>

          <div className="col-12 col-md-4">
            <div className="d-flex justify-content-between text-muted mb-1">
              <span>Similarity Threshold</span>
              <span className="fw-bold text-dark">{Math.round(threshold * 100)}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="0.9"
              step="0.05"
              value={threshold}
              onChange={(e) => setThreshold(Number(e.target.value))}
              className="form-range"
            />
          </div>

          <div className="col-12 col-md-4">
            <div className="text-muted mb-1">Document Scope</div>
            <select
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="form-select form-select-sm rounded-pill"
              style={{ fontSize: '12px', borderColor: '#eaecf0' }}
            >
              <option value="all">All Documents ({documents.length})</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.original_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Results View */}
      <div className="d-flex flex-column gap-3">
        <div className="d-flex align-items-center justify-content-between text-muted" style={{ fontSize: '12px' }}>
          <span>Search Results {searched && `(${results.length} chunks retrieved)`}</span>
        </div>

        {loading ? (
          <div className="py-5 text-center text-muted" style={{ fontSize: '13px' }}>
            <div className="spinner-border spinner-border-sm text-primary mb-2" role="status" />
            <div>Scanning ChromaDB vector space...</div>
          </div>
        ) : searched && results.length === 0 ? (
          <div className="py-5 text-center text-muted" style={{ fontSize: '13px' }}>
            No chunks met the similarity threshold. Try lowering the threshold slider.
          </div>
        ) : (
          <div className="d-flex flex-column gap-2.5">
            {results.map((r, i) => (
              <div key={i} className="app-card p-3">
                <div className="d-flex align-items-center justify-content-between mb-2">
                  <div className="d-flex align-items-center gap-2" style={{ fontSize: '12.5px' }}>
                    <FileText size={15} className="text-primary" />
                    <span className="fw-bold text-dark">{r.document_name}</span>
                    <span className="text-muted">• Page {r.page_number}</span>
                    <span className="text-muted">• Chunk #{r.chunk_index}</span>
                  </div>

                  <div className="d-flex align-items-center gap-2">
                    <span
                      className="badge rounded-pill fw-bold"
                      style={{
                        backgroundColor: '#ecfdf5',
                        color: '#047857',
                        border: '1px solid #a7f3d0',
                        fontSize: '11px'
                      }}
                    >
                      {Math.round(r.similarity_score * 100)}% Match
                    </span>
                    <button
                      onClick={() => setInspectCitation(r)}
                      className="btn btn-link btn-sm p-0 text-primary text-decoration-none fw-semibold"
                      style={{ fontSize: '12px' }}
                    >
                      Inspect Full
                    </button>
                  </div>
                </div>

                <div
                  className="text-secondary"
                  style={{
                    fontSize: '12px',
                    lineHeight: '1.5',
                    fontFamily: 'monospace',
                    backgroundColor: '#fafbfc',
                    padding: '10px 12px',
                    borderRadius: '8px',
                    border: '1px solid #eaecf0',
                    whiteSpace: 'pre-wrap'
                  }}
                >
                  {r.content_snippet}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <CitationModal
        citation={inspectCitation}
        onClose={() => setInspectCitation(null)}
      />
    </div>
  );
}

