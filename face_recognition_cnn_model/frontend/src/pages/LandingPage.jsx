import { Link } from 'react-router-dom';
import { BrainCircuit, Zap, Eye, ChevronRight } from 'lucide-react';
import './LandingPage.css';

export default function LandingPage() {
  return (
    <div className="landing-container animate-fade-in">
      <section className="hero-section text-center">
        <h1 className="hero-title">
          Understand Emotion in <span className="highlight">Real-Time</span>
        </h1>
        <p className="hero-subtitle">
          We built a custom Convolutional Neural Network (CNN) trained on over 30,000 human faces to instantly classify your facial expressions using edge-speed inference.
        </p>
        <Link to="/predict" className="btn-primary hero-btn">
          Launch Live Camera <ChevronRight size={20} />
        </Link>
      </section>

      <section className="features-grid">
        <div className="glass-panel feature-card">
          <div className="icon-wrapper">
            <BrainCircuit size={32} color="#6366f1" />
          </div>
          <h3>Deep Learning Powered</h3>
          <p>Utilizes a custom VGG-style CNN architecture trained from scratch on the FER-2013 dataset.</p>
        </div>
        <div className="glass-panel feature-card">
          <div className="icon-wrapper">
            <Zap size={32} color="#8b5cf6" />
          </div>
          <h3>Instant Inference</h3>
          <p>Your webcam frames are processed securely and classified in milliseconds by our Python API.</p>
        </div>
        <div className="glass-panel feature-card">
          <div className="icon-wrapper">
            <Eye size={32} color="#ec4899" />
          </div>
          <h3>7 Emotion Classes</h3>
          <p>Detects Happy, Sad, Angry, Fearful, Disgusted, Surprised, and Neutral expressions.</p>
        </div>
      </section>
    </div>
  );
}
