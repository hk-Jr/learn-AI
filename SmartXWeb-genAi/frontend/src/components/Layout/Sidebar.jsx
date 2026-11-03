import React from 'react';
import {
  LayoutDashboard,
  FileText,
  MessageSquareText,
  Search,
  Settings,
  Sparkles,
  Database
} from 'lucide-react';

export function Sidebar({ currentTab, setCurrentTab, documentCount }) {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'documents', label: 'Documents', icon: FileText, badge: documentCount > 0 ? documentCount : null },
    { id: 'chat', label: 'AI Assistant', icon: MessageSquareText },
    { id: 'search', label: 'Search Explorer', icon: Search },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="app-sidebar">
      <div>
        {/* Brand */}
        <div className="d-flex align-items-center gap-2 p-4 border-bottom">
          <div
            className="d-flex align-items-center justify-content-center text-white"
            style={{
              width: '36px',
              height: '36px',
              borderRadius: '10px',
              background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
              boxShadow: '0 2px 4px rgba(37, 99, 235, 0.2)'
            }}
          >
            <Sparkles size={18} />
          </div>
          <div>
            <div className="fw-bold text-dark lh-1" style={{ fontSize: '15px' }}>SmartX RAG</div>
            <div className="text-muted" style={{ fontSize: '11px', marginTop: '2px' }}>Enterprise Knowledge</div>
          </div>
        </div>

        {/* Navigation list */}
        <nav className="p-3 d-flex flex-column gap-1">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const active = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setCurrentTab(item.id)}
                className={`nav-btn ${active ? 'active' : ''}`}
              >
                <div className="d-flex align-items-center gap-2.5">
                  <Icon size={17} className={active ? 'text-primary' : 'text-muted'} />
                  <span>{item.label}</span>
                </div>
                {item.badge !== null && (
                  <span
                    className="badge rounded-pill"
                    style={{
                      fontSize: '11px',
                      backgroundColor: active ? '#2563eb' : '#f2f4f7',
                      color: active ? '#ffffff' : '#475467',
                      padding: '4px 8px'
                    }}
                  >
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer Info */}
      <div className="p-3 border-top">
        <div
          className="d-flex align-items-center gap-2 p-2 rounded"
          style={{ backgroundColor: '#f9fafb', border: '1px solid #eaecf0', fontSize: '11.5px' }}
        >
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: '#10b981',
              boxShadow: '0 0 0 2px rgba(16, 185, 129, 0.2)'
            }}
          />
          <div className="text-muted text-truncate">
            <strong className="text-dark">Vector Store:</strong> ChromaDB Ready
          </div>
        </div>
      </div>
    </aside>
  );
}

