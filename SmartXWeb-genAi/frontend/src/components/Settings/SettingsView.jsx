import React, { useState, useEffect } from 'react';
import {
  Key,
  Sliders,
  CheckCircle2,
  Sparkles,
  Save,
  Info
} from 'lucide-react';
import { api } from '../../api/client';

export function SettingsView({ settings, onSettingsUpdated }) {
  const [provider, setProvider] = useState('smart_local');
  const [model, setModel] = useState('gemini-2.5-flash');
  const [chunkSize, setChunkSize] = useState(500);
  const [chunkOverlap, setChunkOverlap] = useState(50);
  const [topK, setTopK] = useState(4);
  const [threshold, setThreshold] = useState(0.3);
  const [geminiKey, setGeminiKey] = useState('');
  const [openaiKey, setOpenaiKey] = useState('');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');

  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);

  useEffect(() => {
    if (settings) {
      setProvider(settings.llm_provider || 'smart_local');
      setModel(settings.llm_model || 'gemini-2.5-flash');
      setChunkSize(settings.chunk_size || 500);
      setChunkOverlap(settings.chunk_overlap || 50);
      setTopK(settings.top_k || 4);
      setThreshold(settings.similarity_threshold || 0.3);
      setOllamaUrl(settings.ollama_base_url || 'http://localhost:11434');
    }
  }, [settings]);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);

    try {
      const payload = {
        llm_provider: provider,
        llm_model: model,
        chunk_size: chunkSize,
        chunk_overlap: chunkOverlap,
        top_k: topK,
        similarity_threshold: threshold,
        ollama_base_url: ollamaUrl,
      };

      if (geminiKey.trim()) payload.gemini_api_key = geminiKey.trim();
      if (openaiKey.trim()) payload.openai_api_key = openaiKey.trim();

      await api.updateSettings(payload);
      setGeminiKey('');
      setOpenaiKey('');
      setSavedSuccess(true);
      onSettingsUpdated();
      setTimeout(() => setSavedSuccess(false), 3000);
    } catch (err) {
      alert('Failed to save settings: ' + err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="container-fluid p-0" style={{ maxWidth: '850px' }}>
      <div className="mb-4">
        <h2 className="h5 fw-bold mb-1 text-dark">System Settings & Model Configuration</h2>
        <p className="text-muted mb-0" style={{ fontSize: '13px' }}>
          Configure AI providers, embeddings, chunking strategies, and retrieval thresholds.
        </p>
      </div>

      <form onSubmit={handleSave} className="d-flex flex-column gap-4">
        {/* Generative AI Provider */}
        <div className="app-card p-4">
          <div className="d-flex align-items-center gap-2 mb-3">
            <Sparkles size={18} className="text-primary" />
            <h3 className="h6 fw-bold mb-0 text-dark">Generative AI Provider</h3>
          </div>

          <div className="row g-2 mb-3">
            {[
              { id: 'smart_local', name: 'Smart Local RAG', desc: 'Zero keys needed, built-in' },
              { id: 'gemini', name: 'Google Gemini', desc: 'Gemini 2.5 Flash / Pro' },
              { id: 'openai', name: 'OpenAI', desc: 'GPT-4o / GPT-4o mini' },
              { id: 'ollama', name: 'Local Ollama', desc: 'Llama 3 / Mistral' },
            ].map((p) => {
              const active = provider === p.id;
              return (
                <div key={p.id} className="col-12 col-sm-6 col-md-3">
                  <button
                    type="button"
                    onClick={() => {
                      setProvider(p.id);
                      if (p.id === 'gemini') setModel('gemini-2.5-flash');
                      if (p.id === 'openai') setModel('gpt-4o-mini');
                      if (p.id === 'ollama') setModel('llama3');
                    }}
                    className="w-100 p-3 rounded-3 text-start border transition"
                    style={{
                      backgroundColor: active ? '#eff6ff' : '#ffffff',
                      borderColor: active ? '#2563eb' : '#eaecf0',
                      boxShadow: active ? '0 0 0 2px rgba(37, 99, 235, 0.15)' : 'none',
                      cursor: 'pointer'
                    }}
                  >
                    <div className={`fw-bold ${active ? 'text-primary' : 'text-dark'}`} style={{ fontSize: '12.5px' }}>
                      {p.name}
                    </div>
                    <div className="text-muted" style={{ fontSize: '11px', marginTop: '2px' }}>
                      {p.desc}
                    </div>
                  </button>
                </div>
              );
            })}
          </div>

          <div style={{ fontSize: '12px' }}>
            <label className="fw-semibold text-secondary mb-1">Model Identifier</label>
            <input
              type="text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
              className="form-control form-control-sm"
              style={{ fontSize: '12.5px', borderColor: '#eaecf0', borderRadius: '8px' }}
            />
          </div>
        </div>

        {/* API Credentials */}
        <div className="app-card p-4">
          <div className="d-flex align-items-center gap-2 mb-3">
            <Key size={18} className="text-primary" />
            <h3 className="h6 fw-bold mb-0 text-dark">API Keys & Endpoints</h3>
          </div>

          <div className="d-flex flex-column gap-3" style={{ fontSize: '12px' }}>
            {/* Gemini */}
            <div>
              <div className="d-flex align-items-center justify-content-between mb-1">
                <label className="fw-semibold text-secondary">Google Gemini API Key</label>
                {settings?.has_gemini_key ? (
                  <span className="text-success fw-semibold d-flex align-items-center gap-1" style={{ fontSize: '11px' }}>
                    <CheckCircle2 size={12} />
                    Key Stored & Active
                  </span>
                ) : (
                  <span className="text-muted" style={{ fontSize: '11px' }}>Not configured</span>
                )}
              </div>
              <input
                type="password"
                placeholder={settings?.has_gemini_key ? '•••••••••••••••• (Leave blank to keep existing)' : 'Enter GEMINI_API_KEY'}
                value={geminiKey}
                onChange={(e) => setGeminiKey(e.target.value)}
                className="form-control form-control-sm"
                style={{ fontSize: '12.5px', borderColor: '#eaecf0', borderRadius: '8px' }}
              />
            </div>

            {/* OpenAI */}
            <div>
              <div className="d-flex align-items-center justify-content-between mb-1">
                <label className="fw-semibold text-secondary">OpenAI API Key</label>
                {settings?.has_openai_key ? (
                  <span className="text-success fw-semibold d-flex align-items-center gap-1" style={{ fontSize: '11px' }}>
                    <CheckCircle2 size={12} />
                    Key Stored & Active
                  </span>
                ) : (
                  <span className="text-muted" style={{ fontSize: '11px' }}>Not configured</span>
                )}
              </div>
              <input
                type="password"
                placeholder={settings?.has_openai_key ? '•••••••••••••••• (Leave blank to keep existing)' : 'Enter sk-... API Key'}
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                className="form-control form-control-sm"
                style={{ fontSize: '12.5px', borderColor: '#eaecf0', borderRadius: '8px' }}
              />
            </div>

            {/* Ollama URL */}
            <div>
              <label className="fw-semibold text-secondary mb-1">Ollama Base URL</label>
              <input
                type="text"
                value={ollamaUrl}
                onChange={(e) => setOllamaUrl(e.target.value)}
                className="form-control form-control-sm"
                style={{ fontSize: '12.5px', borderColor: '#eaecf0', borderRadius: '8px' }}
              />
            </div>
          </div>
        </div>

        {/* Chunking & Retrieval Parameters */}
        <div className="app-card p-4">
          <div className="d-flex align-items-center gap-2 mb-3">
            <Sliders size={18} className="text-primary" />
            <h3 className="h6 fw-bold mb-0 text-dark">Chunking & Retrieval Parameters</h3>
          </div>

          <div className="row g-4" style={{ fontSize: '12px' }}>
            <div className="col-12 col-md-6">
              <div className="d-flex justify-content-between mb-1 fw-semibold text-secondary">
                <span>Chunk Size (characters)</span>
                <span className="text-primary font-monospace">{chunkSize} chars</span>
              </div>
              <input
                type="range"
                min="200"
                max="2000"
                step="50"
                value={chunkSize}
                onChange={(e) => setChunkSize(Number(e.target.value))}
                className="form-range"
              />
              <div className="text-muted" style={{ fontSize: '11px' }}>Recommended: 500 characters</div>
            </div>

            <div className="col-12 col-md-6">
              <div className="d-flex justify-content-between mb-1 fw-semibold text-secondary">
                <span>Chunk Overlap (characters)</span>
                <span className="text-primary font-monospace">{chunkOverlap} chars</span>
              </div>
              <input
                type="range"
                min="0"
                max="300"
                step="10"
                value={chunkOverlap}
                onChange={(e) => setChunkOverlap(Number(e.target.value))}
                className="form-range"
              />
              <div className="text-muted" style={{ fontSize: '11px' }}>Preserves context across chunk boundaries</div>
            </div>

            <div className="col-12 col-md-6">
              <div className="d-flex justify-content-between mb-1 fw-semibold text-secondary">
                <span>Top-K Chunks Retrieved</span>
                <span className="text-primary font-monospace">{topK}</span>
              </div>
              <input
                type="range"
                min="1"
                max="10"
                value={topK}
                onChange={(e) => setTopK(Number(e.target.value))}
                className="form-range"
              />
              <div className="text-muted" style={{ fontSize: '11px' }}>Number of nearest neighbor chunks</div>
            </div>

            <div className="col-12 col-md-6">
              <div className="d-flex justify-content-between mb-1 fw-semibold text-secondary">
                <span>Similarity Threshold</span>
                <span className="text-primary font-monospace">{Math.round(threshold * 100)}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="0.8"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(Number(e.target.value))}
                className="form-range"
              />
              <div className="text-muted" style={{ fontSize: '11px' }}>Minimum similarity to prevent hallucination</div>
            </div>
          </div>
        </div>

        {/* Submit Bar */}
        <div className="d-flex align-items-center justify-content-between pt-2">
          {savedSuccess ? (
            <div className="text-success fw-bold d-flex align-items-center gap-1.5" style={{ fontSize: '12.5px' }}>
              <CheckCircle2 size={16} />
              <span>Settings saved successfully!</span>
            </div>
          ) : (
            <div className="text-muted d-flex align-items-center gap-1.5" style={{ fontSize: '12px' }}>
              <Info size={14} />
              <span>Keys are saved securely on backend</span>
            </div>
          )}

          <button
            type="submit"
            disabled={saving}
            className="btn btn-primary d-flex align-items-center gap-2 px-4 py-2 fw-semibold"
            style={{ borderRadius: '8px', fontSize: '12.5px', backgroundColor: '#2563eb', borderColor: '#2563eb' }}
          >
            <Save size={15} />
            <span>{saving ? 'Saving...' : 'Save Configuration'}</span>
          </button>
        </div>
      </form>
    </div>
  );
}

