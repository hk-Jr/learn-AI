import React from 'react';
import { UploadCloud, MessageSquarePlus, Sparkles } from 'lucide-react';

export function Header({ currentTab, settings, onQuickUpload, onNewChat }) {
  const getTitle = () => {
    switch (currentTab) {
      case 'dashboard':
        return 'System Overview & Analytics';
      case 'documents':
        return 'Knowledge Base & Ingestion';
      case 'chat':
        return 'AI Grounded Question Answering';
      case 'search':
        return 'Semantic Retrieval Explorer';
      case 'settings':
        return 'System Configuration & Models';
      default:
        return 'RAG Platform';
    }
  };

  const getProviderBadge = () => {
    if (!settings) return null;
    const provider = settings.llm_provider;
    let label = 'Smart Local Grounded';

    if (provider === 'gemini') {
      label = `Gemini (${settings.llm_model})`;
    } else if (provider === 'openai') {
      label = `OpenAI (${settings.llm_model})`;
    } else if (provider === 'ollama') {
      label = `Ollama (${settings.llm_model})`;
    }

    return (
      <div
        className="d-none d-md-flex align-items-center gap-1.5 px-2.5 py-1 rounded-pill"
        style={{
          fontSize: '11.5px',
          fontWeight: '500',
          backgroundColor: '#eff6ff',
          color: '#1d4ed8',
          border: '1px solid #bfdbfe'
        }}
      >
        <Sparkles size={13} />
        <span>{label}</span>
      </div>
    );
  };

  return (
    <header className="app-header">
      <div className="d-flex align-items-center gap-3">
        <h1 className="h6 mb-0 fw-bold text-dark">{getTitle()}</h1>
        {getProviderBadge()}
      </div>

      <div className="d-flex align-items-center gap-2">
        <button
          onClick={onQuickUpload}
          className="btn btn-outline-secondary btn-sm d-flex align-items-center gap-1.5"
          style={{ fontSize: '12.5px', borderRadius: '8px', padding: '6px 12px' }}
        >
          <UploadCloud size={15} className="text-primary" />
          <span>Upload</span>
        </button>

        <button
          onClick={onNewChat}
          className="btn btn-primary btn-sm d-flex align-items-center gap-1.5"
          style={{
            fontSize: '12.5px',
            borderRadius: '8px',
            backgroundColor: '#2563eb',
            borderColor: '#2563eb',
            padding: '6px 14px'
          }}
        >
          <MessageSquarePlus size={15} />
          <span>New Chat</span>
        </button>
      </div>
    </header>
  );
}

