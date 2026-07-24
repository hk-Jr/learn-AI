import { useState, useRef, useEffect } from 'react';
import { Camera, CameraOff, Brain } from 'lucide-react';
import './PredictionPage.css';

export default function PredictionPage() {
  const [isCameraActive, setIsCameraActive] = useState(false);
  const [predictionData, setPredictionData] = useState(null);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const intervalRef = useRef(null);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraActive(true);
        // Start sending frames to backend every 300ms
        intervalRef.current = setInterval(sendFrameToBackend, 300);
      }
    } catch (err) {
      console.error("Error accessing camera: ", err);
      alert("Could not access the camera. Please ensure you have granted permissions.");
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
    }
    setIsCameraActive(false);
    setPredictionData(null);
  };

  const sendFrameToBackend = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    
    // Set canvas dimensions to match video
    if (video.videoWidth === 0) return;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw current video frame to canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to base64 jpeg
    const base64Image = canvas.toDataURL('image/jpeg', 0.8);
    
    try {
      const response = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image_base64: base64Image })
      });
      
      const data = await response.json();
      if (data && data.prediction) {
        setPredictionData(data);
      }
    } catch (error) {
      console.error("Backend connection error:", error);
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => stopCamera();
  }, []);

  const emotions = ['happy', 'neutral', 'surprise', 'sad', 'angry', 'fear', 'disgust'];

  return (
    <div className="prediction-container animate-fade-in">
      <div className="header-section text-center">
        <h2>Live Emotion Recognition</h2>
        <p>Grant camera access to see the AI analyze your expressions in real-time.</p>
      </div>

      <div className="dashboard-grid">
        {/* Camera Feed Section */}
        <div className="glass-panel video-panel">
          <div className={`video-wrapper ${!isCameraActive ? 'inactive' : ''}`}>
            {!isCameraActive && (
              <div className="camera-prompt">
                <CameraOff size={48} color="#a0a0a8" />
                <p>Camera is currently off</p>
                <button className="btn-primary" onClick={startCamera}>
                  <Camera size={20} /> Enable Camera
                </button>
              </div>
            )}
            
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              className="live-video"
              style={{ display: isCameraActive ? 'block' : 'none' }}
            />
            
            {/* Hidden canvas for capturing frames */}
            <canvas ref={canvasRef} style={{ display: 'none' }} />
          </div>
          {isCameraActive && (
            <button className="btn-danger mt-4" onClick={stopCamera}>
              <CameraOff size={20} /> Stop Camera
            </button>
          )}
        </div>

        {/* Prediction Results Section */}
        <div className="glass-panel results-panel">
          <div className="results-header">
            <Brain size={24} color="#ec4899" />
            <h3>AI Analysis</h3>
          </div>
          
          <div className="current-emotion">
            <span className="emotion-label">
              {predictionData ? predictionData.prediction : "Waiting for signal..."}
            </span>
            <div className="confidence-bar-bg">
              <div 
                className="confidence-bar-fill" 
                style={{ width: `${predictionData ? predictionData.confidence : 0}%` }}
              ></div>
            </div>
            <span className="confidence-text">
              {predictionData ? `${predictionData.confidence.toFixed(1)}% Confidence` : "0% Confidence"}
            </span>
          </div>

          <div className="emotion-list">
            <p className="list-title">Probability Distribution</p>
            {emotions.map((emotion) => {
              const prob = predictionData?.probabilities?.[emotion] || 0;
              return (
                <div key={emotion} className="emotion-item">
                  <span style={{ textTransform: 'capitalize' }}>{emotion}</span>
                  <span className="emotion-value">{prob.toFixed(1)}%</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
