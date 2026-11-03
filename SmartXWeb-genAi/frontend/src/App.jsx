import React, { useState, useEffect } from 'react';
import { Sidebar } from './components/Layout/Sidebar';
import { Header } from './components/Layout/Header';
import { DashboardView } from './components/Dashboard/DashboardView';
import { DocumentsView } from './components/Documents/DocumentsView';
import { ChatView } from './components/Chat/ChatView';
import { SearchView } from './components/Search/SearchView';
import { SettingsView } from './components/Settings/SettingsView';
import { api } from './api/client';

export function App() {
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [stats, setStats] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [systemSettings, setSystemSettings] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadData = async () => {
    setLoading(true);
    try {
      const [s, docs, cfg] = await Promise.all([
        api.getDashboardStats().catch(() => null),
        api.getDocuments().catch(() => []),
        api.getSettings().catch(() => null),
      ]);
      setStats(s);
      setDocuments(docs);
      setSystemSettings(cfg);
    } catch (err) {
      console.error('Failed to load initial data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleQuickUpload = () => {
    setCurrentTab('documents');
  };

  const handleNewChat = () => {
    setCurrentTab('chat');
  };

  return (
    <div className="app-shell">
      {/* Sidebar Navigation */}
      <Sidebar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        documentCount={documents.length}
      />

      {/* Main Content Area */}
      <div className="app-content">
        <Header
          currentTab={currentTab}
          settings={systemSettings}
          onQuickUpload={handleQuickUpload}
          onNewChat={handleNewChat}
        />

        <main className="app-main-view">
          {currentTab === 'dashboard' && (
            <DashboardView
              stats={stats}
              loading={loading}
              onNavigate={setCurrentTab}
              onUploadSuccess={loadData}
            />
          )}

          {currentTab === 'documents' && (
            <DocumentsView
              documents={documents}
              loading={loading}
              onRefresh={loadData}
            />
          )}

          {currentTab === 'chat' && (
            <ChatView
              documents={documents}
            />
          )}

          {currentTab === 'search' && (
            <SearchView
              documents={documents}
            />
          )}

          {currentTab === 'settings' && (
            <SettingsView
              settings={systemSettings}
              onSettingsUpdated={loadData}
            />
          )}
        </main>
      </div>
    </div>
  );
}

export default App;

