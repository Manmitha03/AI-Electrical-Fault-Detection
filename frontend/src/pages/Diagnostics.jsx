import React, { useState } from 'react';
import { UploadCloud, CheckCircle, AlertTriangle, ShieldAlert, Cpu } from 'lucide-react';
import { endpoints, fetchApi } from '../api';
import './Diagnostics.css';

const Diagnostics = () => {
  const [activeTab, setActiveTab] = useState('sensor'); // 'sensor' or 'image'
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  // Sensor Form State
  const [sensorData, setSensorData] = useState({
    voltage: 230,
    current: 12,
    temperature: 45,
    power: 2500,
    power_factor: 0.95,
    frequency: 50,
    resistance: 25,
    vibration: 0.05,
    symptoms: ''
  });

  // Image Upload State
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [imageSymptoms, setImageSymptoms] = useState('');

  const handleSensorChange = (e) => {
    const { name, value } = e.target;
    setSensorData(prev => ({
      ...prev,
      [name]: name === 'symptoms' ? value : parseFloat(value) || 0
    }));
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviewUrl(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const submitSensorDiagnosis = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);
    try {
      const data = await fetchApi(endpoints.diagnoseSensor, {
        method: 'POST',
        body: JSON.stringify(sensorData)
      });
      setResult(data);
    } catch (err) {
      alert('Diagnosis failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const submitImageDiagnosis = async (e) => {
    e.preventDefault();
    if (!selectedFile) return;
    
    setLoading(true);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (imageSymptoms) {
        formData.append('symptoms', imageSymptoms);
      }

      const response = await fetch(endpoints.diagnoseImage, {
        method: 'POST',
        body: formData
      });
      
      if (!response.ok) throw new Error('API Error');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      alert('Diagnosis failed: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;

    const isNormal = result.fault_type === 'Normal';
    
    return (
      <div className="glass-panel p-6 mt-6 animate-slide-up">
        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
          {isNormal ? <CheckCircle color="var(--status-normal)" /> : <AlertTriangle color="var(--status-critical)" />}
          Diagnostic Report
        </h2>
        
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="result-stat">
            <span className="text-muted text-sm">Detected Fault</span>
            <h3 className={`text-lg font-bold ${isNormal ? 'text-accent' : 'text-danger'}`}>
              {result.fault_type}
            </h3>
          </div>
          <div className="result-stat">
            <span className="text-muted text-sm">AI Confidence</span>
            <h3 className="text-lg font-bold">{(result.confidence * 100).toFixed(1)}%</h3>
          </div>
          <div className="result-stat">
            <span className="text-muted text-sm">Severity Level</span>
            <h3 className="text-lg font-bold">
              <span className={`badge badge-${result.severity.toLowerCase()}`}>
                {result.severity}
              </span>
            </h3>
          </div>
          <div className="result-stat">
            <span className="text-muted text-sm">Risk Score</span>
            <h3 className="text-lg font-bold">{result.risk_score} / 100</h3>
          </div>
        </div>

        {!isNormal && (
          <div className="diagnosis-details flex flex-col gap-4">
            <div className="detail-section">
              <h4 className="font-medium text-warning mb-2 flex items-center gap-2">
                <ShieldAlert size={16} /> Recommended Actions
              </h4>
              <ul className="list-disc pl-5 text-sm">
                {result.recommended_actions.map((act, i) => <li key={i} className="mb-1">{act}</li>)}
              </ul>
            </div>
            
            <div className="detail-section">
              <h4 className="font-medium mb-2">Possible Causes</h4>
              <ul className="list-disc pl-5 text-sm text-muted">
                {result.possible_causes.map((cause, i) => <li key={i} className="mb-1">{cause}</li>)}
              </ul>
            </div>
            
            {result.evidence && result.evidence.length > 0 && (
              <div className="detail-section">
                <h4 className="font-medium mb-2">Evidence Found</h4>
                <ul className="list-disc pl-5 text-sm text-muted">
                  {result.evidence.map((ev, i) => <li key={i} className="mb-1">{ev}</li>)}
                </ul>
              </div>
            )}
          </div>
        )}

        <div className="mt-6 p-4 bg-[rgba(0,0,0,0.3)] rounded-md border border-[rgba(255,255,255,0.1)]">
          <p className="text-xs text-muted leading-relaxed">
            <strong>Disclaimer:</strong> {result.disclaimer}
          </p>
        </div>
      </div>
    );
  };

  return (
    <div className="diagnostics-container animate-fade-in">
      <header className="page-header mb-6">
        <div>
          <h1 className="text-gradient">Diagnostic Engine</h1>
          <p className="text-muted">Multi-modal AI fault analysis</p>
        </div>
      </header>

      <div className="tabs mb-6 flex gap-4">
        <button 
          className={`tab-btn ${activeTab === 'sensor' ? 'active' : ''}`}
          onClick={() => { setActiveTab('sensor'); setResult(null); }}
        >
          <Cpu size={18} /> Sensor Analysis
        </button>
        <button 
          className={`tab-btn ${activeTab === 'image' ? 'active' : ''}`}
          onClick={() => { setActiveTab('image'); setResult(null); }}
        >
          <Camera size={18} /> Visual Analysis
        </button>
      </div>

      <div className="grid grid-cols-2 gap-8">
        <div className="input-section glass-panel p-6">
          {activeTab === 'sensor' ? (
            <form onSubmit={submitSensorDiagnosis} className="flex flex-col gap-4">
              <h3 className="font-medium mb-2">Sensor Parameters</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm text-muted block mb-1">Voltage (V)</label>
                  <input type="number" step="0.1" name="voltage" value={sensorData.voltage} onChange={handleSensorChange} className="input-field" required />
                </div>
                <div>
                  <label className="text-sm text-muted block mb-1">Current (A)</label>
                  <input type="number" step="0.1" name="current" value={sensorData.current} onChange={handleSensorChange} className="input-field" required />
                </div>
                <div>
                  <label className="text-sm text-muted block mb-1">Temperature (°C)</label>
                  <input type="number" step="0.1" name="temperature" value={sensorData.temperature} onChange={handleSensorChange} className="input-field" required />
                </div>
                <div>
                  <label className="text-sm text-muted block mb-1">Power Factor</label>
                  <input type="number" step="0.01" name="power_factor" value={sensorData.power_factor} onChange={handleSensorChange} className="input-field" required />
                </div>
              </div>
              
              <div className="mt-2">
                <label className="text-sm text-muted block mb-1">Symptoms (Optional)</label>
                <textarea 
                  name="symptoms" 
                  value={sensorData.symptoms} 
                  onChange={handleSensorChange} 
                  className="input-field" 
                  rows="3"
                  placeholder="e.g., The motor is making a loud humming noise and getting hot"
                ></textarea>
              </div>
              
              <button type="submit" className="btn btn-primary mt-4" disabled={loading}>
                {loading ? 'Analyzing...' : 'Run Diagnostics'}
              </button>
            </form>
          ) : (
            <form onSubmit={submitImageDiagnosis} className="flex flex-col gap-4">
              <h3 className="font-medium mb-2">Visual Inspection</h3>
              
              <div className="upload-area flex flex-col items-center justify-center p-8 border-2 border-dashed border-[rgba(255,255,255,0.2)] rounded-lg cursor-pointer hover:border-primary transition-colors">
                <input 
                  type="file" 
                  accept="image/*" 
                  onChange={handleFileChange} 
                  className="hidden" 
                  id="image-upload" 
                />
                <label htmlFor="image-upload" className="cursor-pointer flex flex-col items-center">
                  {previewUrl ? (
                    <img src={previewUrl} alt="Preview" className="max-h-[200px] object-contain mb-4 rounded" />
                  ) : (
                    <UploadCloud size={48} className="text-muted mb-4" />
                  )}
                  <span className="text-primary font-medium">{previewUrl ? 'Change Image' : 'Click to Upload Image'}</span>
                  <span className="text-xs text-muted mt-1">Supports JPG, PNG</span>
                </label>
              </div>
              
              <div className="mt-2">
                <label className="text-sm text-muted block mb-1">Context / Symptoms (Optional)</label>
                <input 
                  type="text" 
                  value={imageSymptoms} 
                  onChange={(e) => setImageSymptoms(e.target.value)} 
                  className="input-field" 
                  placeholder="e.g., Found near the main breaker panel"
                />
              </div>
              
              <button type="submit" className="btn btn-primary mt-4" disabled={loading || !selectedFile}>
                {loading ? 'Analyzing Image...' : 'Run Visual Diagnostics'}
              </button>
            </form>
          )}
        </div>

        <div className="results-section">
          {renderResult()}
          {!result && !loading && (
            <div className="h-full flex items-center justify-center text-muted border border-dashed border-[rgba(255,255,255,0.1)] rounded-lg p-6 text-center">
              Submit sensor readings or an image to see diagnostic results.
            </div>
          )}
          {loading && (
            <div className="h-full flex flex-col items-center justify-center gap-4 text-primary">
              <div className="spinner"></div>
              <span>Processing data through AI models...</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Diagnostics;
