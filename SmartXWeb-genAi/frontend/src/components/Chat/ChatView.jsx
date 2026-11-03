import React, { useState, useEffect, useRef } from 'react';
import {
  Send,
  MessageSquare,
  Plus,
  Trash2,
  Copy,
  Check,
  BookOpen,
  Filter,
  Clock,
  Search,
  BrainCircuit,
  ArrowUp,
  FileText
} from 'lucide-react';
import { api } from '../../api/client';
import { CitationModal } from './CitationModal';
import { AIAssistantHero } from '../ui/AIAssistantHero';

export function ChatView({ documents }) {
  const [conversations, setConversations] = useState([]);
  const [activeConvId, setActiveConvId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedDocFilter, setSelectedDocFilter] = useState('all');
  const [selectedProvider, setSelectedProvider] = useState('auto');
  const [selectedCitation, setSelectedCitation] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  // Reference component toggles
  const [searchEnabled, setSearchEnabled] = useState(true);
  const [deepResearchEnabled, setDeepResearchEnabled] = useState(false);
  const [reasonEnabled, setReasonEnabled] = useState(true);

  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    if (activeConvId) {
      loadMessages(activeConvId);
    } else {
      setMessages([]);
    }
  }, [activeConvId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const loadConversations = async () => {
    try {
      const convs = await api.getConversations();
      setConversations(convs);
      if (convs.length > 0 && !activeConvId) {
        setActiveConvId(convs[0].id);
      }
    } catch (err) {
      console.error('Failed to load conversations:', err);
    }
  };

  const loadMessages = async (id) => {
    try {
      const conv = await api.getConversation(id);
      setMessages(conv.messages || []);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await api.createConversation('New Question');
      setConversations([newConv, ...conversations]);
      setActiveConvId(newConv.id);
      setMessages([]);
    } catch (err) {
      console.error('Failed to create new conversation:', err);
    }
  };

  const handleDeleteConversation = async (e, id) => {
    e.stopPropagation();
    try {
      await api.deleteConversation(id);
      const remaining = conversations.filter((c) => c.id !== id);
      setConversations(remaining);
      if (activeConvId === id) {
        setActiveConvId(remaining.length > 0 ? remaining[0].id : null);
      }
    } catch (err) {
      console.error('Failed to delete conversation:', err);
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm('Are you sure you want to clear all conversation history?')) return;
    try {
      await api.clearConversations();
      setConversations([]);
      setActiveConvId(null);
      setMessages([]);
    } catch (err) {
      console.error('Failed to clear conversations:', err);
    }
  };

  const handleSend = async (overrideText) => {
    const textToSend = overrideText || inputText;
    if (!textToSend.trim() || loading) return;

    const userText = textToSend.trim();
    setInputText('');

    const tempUserMsg = {
      id: `temp_u_${Date.now()}`,
      conversation_id: activeConvId || 'new',
      role: 'user',
      content: userText,
      created_at: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, tempUserMsg]);
    setLoading(true);

    try {
      const docIds = selectedDocFilter === 'all' ? undefined : [selectedDocFilter];
      const topKValue = deepResearchEnabled ? 6 : 4;
      const providerParam = selectedProvider === 'auto' ? undefined : selectedProvider;

      const res = await api.askQuestion({
        question: userText,
        conversation_id: activeConvId || undefined,
        document_ids: docIds,
        top_k: topKValue,
        provider: providerParam,
      });

      if (!activeConvId || activeConvId !== res.conversation_id) {
        setActiveConvId(res.conversation_id);
        loadConversations();
      }

      const assistantMsg = {
        id: res.assistant_message_id,
        conversation_id: res.conversation_id,
        role: 'assistant',
        content: res.answer,
        citations: res.citations,
        created_at: new Date().toISOString(),
        latency_ms: res.latency_ms,
        model_used: res.model_used,
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      const errorMsg = {
        id: `err_${Date.now()}`,
        conversation_id: activeConvId || 'error',
        role: 'assistant',
        content: `Error: ${err.message || 'Failed to retrieve grounded answer.'}`,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="d-flex w-100 h-100 overflow-hidden bg-white">
      {/* Sessions Left Drawer */}
      <aside
        className="d-none d-md-flex flex-column justify-content-between border-end"
        style={{ width: '260px', backgroundColor: '#fafbfc' }}
      >
        <div className="p-3 border-bottom d-flex align-items-center justify-content-between">
          <span className="text-muted fw-bold text-uppercase" style={{ fontSize: '11px', letterSpacing: '0.05em' }}>
            Conversations
          </span>
          <button
            onClick={handleNewConversation}
            className="btn btn-primary btn-sm p-1 rounded-circle"
            title="Start new conversation"
            style={{ width: '28px', height: '28px' }}
          >
            <Plus size={15} />
          </button>
        </div>

        {/* Sessions list */}
        <div className="p-2 overflow-y-auto flex-grow-1 d-flex flex-column gap-1">
          {conversations.length === 0 ? (
            <div className="py-5 text-center text-muted" style={{ fontSize: '12px' }}>
              No chats yet.
            </div>
          ) : (
            conversations.map((c) => {
              const active = c.id === activeConvId;
              return (
                <div
                  key={c.id}
                  onClick={() => setActiveConvId(c.id)}
                  className="d-flex align-items-center justify-content-between p-2 rounded-3 cursor-pointer"
                  style={{
                    backgroundColor: active ? '#eff6ff' : 'transparent',
                    color: active ? '#1d4ed8' : '#344054',
                    border: active ? '1px solid #bfdbfe' : '1px solid transparent',
                    cursor: 'pointer',
                    fontSize: '12.5px',
                    fontWeight: active ? '600' : '400',
                    transition: 'all 0.15s ease'
                  }}
                >
                  <div className="d-flex align-items-center gap-2 text-truncate">
                    <MessageSquare size={14} className={active ? 'text-primary' : 'text-muted'} />
                    <span className="text-truncate">{c.title || 'Conversation'}</span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteConversation(e, c.id)}
                    className="btn btn-link btn-sm p-0 text-muted"
                    title="Delete chat"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              );
            })
          )}
        </div>

        {conversations.length > 0 && (
          <div className="p-2 border-top">
            <button
              onClick={handleClearAll}
              className="btn btn-link btn-sm w-100 text-muted d-flex align-items-center justify-content-center gap-1 text-decoration-none"
              style={{ fontSize: '12px' }}
            >
              <Trash2 size={13} />
              <span>Clear All History</span>
            </button>
          </div>
        )}
      </aside>

      {/* Main Chat Interface */}
      <div className="d-flex flex-column flex-grow-1 overflow-hidden bg-white">
        {/* Scope Header */}
        <div className="px-4 py-2 border-bottom d-flex align-items-center justify-content-between" style={{ backgroundColor: '#ffffff', fontSize: '12px' }}>
          <div className="d-flex align-items-center gap-2">
            <Filter size={14} className="text-primary" />
            <span className="fw-semibold text-secondary">Knowledge Scope:</span>
            <select
              value={selectedDocFilter}
              onChange={(e) => setSelectedDocFilter(e.target.value)}
              className="form-select form-select-sm py-1 px-2 rounded-pill"
              style={{ width: 'auto', fontSize: '12px', borderColor: '#eaecf0' }}
            >
              <option value="all">All Documents ({documents.length})</option>
              {documents.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.original_name}
                </option>
              ))}
            </select>

            <span className="text-muted ms-2 me-1">•</span>
            <span className="fw-semibold text-secondary">LLM Router:</span>
            <select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              className="form-select form-select-sm py-1 px-2 rounded-pill"
              style={{ width: 'auto', fontSize: '12px', borderColor: '#eaecf0' }}
            >
              <option value="auto">Auto (Task-Based Intent Router)</option>
              <option value="gemini">Google Gemini (Gemini 2.5 Flash)</option>
              <option value="ollama">Ollama (Local Models / CodeLlama)</option>
              <option value="openai">OpenAI (GPT-4o-mini)</option>
              <option value="smart_local">Smart Local Grounded Engine</option>
            </select>
          </div>

          <div className="d-flex align-items-center gap-2 text-muted" style={{ fontSize: '11.5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', backgroundColor: '#10b981' }} />
            <span>Zero Hallucination Grounded Mode</span>
          </div>
        </div>

        {/* Message Thread Scroll Area */}
        <div className="flex-grow-1 overflow-y-auto p-4 d-flex flex-column gap-4 bg-white">
          {messages.length === 0 ? (
            <AIAssistantHero
              onSelectPrompt={(prompt) => handleSend(prompt)}
              onToggleSearch={() => setSearchEnabled(!searchEnabled)}
              searchActive={searchEnabled}
            />
          ) : (
            messages.map((m) => {
              const isUser = m.role === 'user';
              return (
                <div
                  key={m.id}
                  className={`d-flex flex-column ${isUser ? 'align-items-end' : 'align-items-start'} gap-1`}
                >
                  <div
                    className="p-3 rounded-4 shadow-sm"
                    style={{
                      maxWidth: '700px',
                      fontSize: '13px',
                      lineHeight: '1.6',
                      backgroundColor: isUser ? '#2563eb' : '#ffffff',
                      color: isUser ? '#ffffff' : '#101828',
                      border: isUser ? 'none' : '1px solid #eaecf0',
                      borderBottomRightRadius: isUser ? '4px' : '16px',
                      borderBottomLeftRadius: isUser ? '16px' : '4px',
                      whiteSpace: 'pre-wrap'
                    }}
                  >
                    {m.content}

                    {!isUser && (
                      <div className="d-flex align-items-center justify-content-between pt-2 mt-2 border-top text-muted" style={{ fontSize: '11px' }}>
                        <div className="d-flex align-items-center gap-2">
                          {m.model_used && <span>{m.model_used}</span>}
                          {m.latency_ms !== undefined && (
                            <span className="d-flex align-items-center gap-1">
                              <Clock size={11} />
                              <span>{m.latency_ms} ms</span>
                            </span>
                          )}
                        </div>
                        <button
                          onClick={() => handleCopy(m.id, m.content)}
                          className="btn btn-link btn-sm p-0 text-muted d-flex align-items-center gap-1 text-decoration-none"
                          style={{ fontSize: '11px' }}
                        >
                          {copiedId === m.id ? (
                            <>
                              <Check size={12} className="text-success" />
                              <span className="text-success">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy size={12} />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Citation Pills */}
                  {!isUser && m.citations && m.citations.length > 0 && (
                    <div className="d-flex flex-wrap gap-1.5 mt-1" style={{ maxWidth: '700px' }}>
                      {m.citations.map((cite, cIdx) => (
                        <button
                          key={cIdx}
                          onClick={() => setSelectedCitation(cite)}
                          className="btn btn-sm py-1 px-2.5 rounded-pill d-inline-flex align-items-center gap-1.5 text-secondary"
                          style={{
                            fontSize: '11px',
                            backgroundColor: '#ffffff',
                            border: '1px solid #eaecf0',
                            boxShadow: '0 1px 2px rgba(16, 24, 40, 0.04)'
                          }}
                        >
                          <BookOpen size={12} className="text-primary" />
                          <span className="text-truncate" style={{ maxWidth: '140px' }}>{cite.document_name}</span>
                          <span className="text-muted">• P.{cite.page_number}</span>
                          <span className="badge rounded-pill bg-light text-primary fw-bold" style={{ fontSize: '9.5px', border: '1px solid #bfdbfe' }}>
                            {Math.round(cite.similarity_score * 100)}%
                          </span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              );
            })
          )}

          {loading && (
            <div className="d-flex align-items-center gap-2 p-2 text-muted" style={{ fontSize: '12px' }}>
              <div className="spinner-border spinner-border-sm text-primary" role="status" />
              <span>Retrieving relevant chunks and synthesizing grounded answer...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Composer inspired by the reference design */}
        <div className="p-3 border-top bg-white">
          <div className="mx-auto" style={{ maxWidth: '760px' }}>
            <div className="ai-input-card">
              {/* Text Input */}
              <div className="p-3">
                <input
                  ref={inputRef}
                  type="text"
                  placeholder="Ask me anything about your documents..."
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyDown={handleKeyDown}
                  disabled={loading}
                  className="w-100 border-0 outline-0 shadow-none bg-transparent"
                  style={{ outline: 'none', fontSize: '14px', color: '#101828' }}
                />
              </div>

              {/* Action Buttons & Badges */}
              <div className="px-3 pb-3 d-flex align-items-center justify-content-between">
                {/* Feature Toggles */}
                <div className="d-flex align-items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setSearchEnabled(!searchEnabled)}
                    className={`pill-toggle-btn ${searchEnabled ? 'active' : 'inactive'}`}
                  >
                    <Search size={14} />
                    <span>Search</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setDeepResearchEnabled(!deepResearchEnabled)}
                    className={`pill-toggle-btn ${deepResearchEnabled ? 'active' : 'inactive'}`}
                  >
                    <svg
                      width="14"
                      height="14"
                      viewBox="0 0 16 16"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="2" />
                      <circle cx="8" cy="8" r="3" fill="currentColor" />
                    </svg>
                    <span>Deep Research</span>
                  </button>

                  <button
                    type="button"
                    onClick={() => setReasonEnabled(!reasonEnabled)}
                    className={`pill-toggle-btn ${reasonEnabled ? 'active' : 'inactive'}`}
                  >
                    <BrainCircuit size={14} />
                    <span>Reason</span>
                  </button>
                </div>

                {/* Send Button */}
                <button
                  type="button"
                  onClick={() => handleSend()}
                  disabled={!inputText.trim() || loading}
                  className="round-btn primary"
                  title="Send Question"
                >
                  <ArrowUp size={16} />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Citation Modal */}
      <CitationModal
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
}

