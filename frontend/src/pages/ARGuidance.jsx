import React, { useState } from 'react';
import { Camera, Maximize, Target, Zap, CheckCircle } from 'lucide-react';
import './ARGuidance.css';

const ARGuidance = () => {
  const [arActive, setArActive] = useState(false);
  const [scanState, setScanState] = useState('idle'); // idle, scanning, found

  const toggleAR = () => {
    if (!arActive) {
      setArActive(true);
      setScanState('scanning');
      
      // Simulate AR detection process
      setTimeout(() => {
        setScanState('found');
      }, 3000);
    } else {
      setArActive(false);
      setScanState('idle');
    }
  };

  return (
    <div className="ar-container h-full flex flex-col animate-fade-in">
      <header className="page-header mb-6">
        <div>
          <h1 className="text-gradient">AR Repair Guidance</h1>
          <p className="text-muted">Augmented Reality visual inspection and repair overlay</p>
        </div>
      </header>

      <div className="glass-panel flex-1 flex flex-col overflow-hidden relative">
        {!arActive ? (
          <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
            <div className="w-24 h-24 rounded-full bg-[rgba(59,130,246,0.1)] flex items-center justify-center mb-6">
              <Camera size={48} color="var(--primary)" />
            </div>
            <h2 className="text-2xl font-bold mb-4">Initialize AR Diagnostics</h2>
            <p className="text-muted max-w-md mb-8">
              Use your device camera to scan electrical panels and components. 
              The AI will overlay thermal data, identify components, and highlight potential faults in real-time.
            </p>
            <button className="btn btn-primary btn-lg" onClick={toggleAR}>
              <Maximize size={20} /> Start AR Camera Session
            </button>
            <p className="text-xs text-muted mt-4 opacity-70">
              * Note: This is a simulated AR view for demonstration purposes.
            </p>
          </div>
        ) : (
          <div className="ar-view flex-1 relative bg-black">
            {/* Simulated Camera Feed Background */}
            <div className="camera-feed-placeholder w-full h-full opacity-60">
              <div className="grid-overlay"></div>
            </div>

            {/* AR UI Elements */}
            <div className="absolute top-4 right-4 flex gap-2">
              <span className="badge badge-normal animate-pulse">Live Feed</span>
              <button className="btn btn-outline text-xs p-1" onClick={toggleAR}>Close</button>
            </div>

            <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2">
              {scanState === 'scanning' && (
                <div className="flex flex-col items-center">
                  <div className="scanning-reticle mb-4">
                    <Target size={64} className="animate-spin text-primary opacity-70" style={{animationDuration: '3s'}} />
                  </div>
                  <div className="bg-[rgba(0,0,0,0.6)] px-4 py-2 rounded-full text-primary font-medium text-sm animate-pulse border border-primary">
                    Scanning for electrical components...
                  </div>
                </div>
              )}

              {scanState === 'found' && (
                <div className="detected-component relative">
                  {/* Bounding Box */}
                  <div className="bounding-box w-64 h-64 border-2 border-warning absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-[rgba(245,158,11,0.1)] rounded">
                    <div className="absolute -top-3 -right-3 w-6 h-6 bg-warning text-black rounded-full flex items-center justify-center font-bold">!</div>
                  </div>
                  
                  {/* AR Info Card Overlay */}
                  <div className="ar-info-card absolute left-36 top-0 w-64 glass-card p-4 animate-slide-up">
                    <div className="flex justify-between items-center mb-2 border-b border-[rgba(255,255,255,0.1)] pb-2">
                      <h4 className="font-bold text-sm">Industrial Motor (M2)</h4>
                      <span className="badge badge-warning text-[10px]">Overheating</span>
                    </div>
                    
                    <div className="flex flex-col gap-2 mb-3">
                      <div className="flex justify-between text-xs">
                        <span className="text-muted">Est. Surface Temp:</span>
                        <span className="text-warning font-bold">85.4°C</span>
                      </div>
                      <div className="flex justify-between text-xs">
                        <span className="text-muted">Thermal Status:</span>
                        <span className="text-warning font-bold">Critical High</span>
                      </div>
                    </div>
                    
                    <div className="ar-actions pt-2 border-t border-[rgba(255,255,255,0.1)]">
                      <button className="btn btn-primary w-full text-xs py-1">View Repair Steps</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
            
            {scanState === 'found' && (
              <div className="absolute bottom-6 left-1/2 transform -translate-x-1/2 bg-[rgba(0,0,0,0.7)] px-6 py-3 rounded-full border border-[rgba(255,255,255,0.2)] flex gap-6 backdrop-blur">
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle size={16} className="text-accent" /> <span className="text-muted">Component Identified</span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <Zap size={16} className="text-warning" /> <span className="text-muted">Thermal Anomaly Detected</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ARGuidance;
