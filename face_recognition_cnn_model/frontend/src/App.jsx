import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Activity } from 'lucide-react';
import LandingPage from './pages/LandingPage';
import PredictionPage from './pages/PredictionPage';
import './index.css';

function App() {
  return (
    <Router>
      <header className="app-header">
        <Link to="/" className="app-logo">
          <Activity size={24} color="#6366f1" />
          Neural<span>Face</span>
        </Link>
        <nav>
          <Link to="/predict" className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.9rem' }}>
            Try it out
          </Link>
        </nav>
      </header>
      
      <main className="main-content">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/predict" element={<PredictionPage />} />
        </Routes>
      </main>
    </Router>
  );
}

export default App;
