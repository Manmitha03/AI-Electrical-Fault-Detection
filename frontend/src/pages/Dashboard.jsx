import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { AlertTriangle, Activity, Zap, Thermometer, ShieldAlert } from 'lucide-react';
import { wsEndpoint, endpoints, fetchApi } from '../api';
import './Dashboard.css';

const Dashboard = () => {
  const [deviceData, setDeviceData] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState(null);
  const [wsStatus, setWsStatus] = useState('connecting');

  useEffect(() => {
    // Initial stats fetch
    fetchApi(endpoints.statistics)
      .then(data => setStats(data))
      .catch(err => console.error('Failed to fetch stats', err));

    // WebSocket connection
    let ws = new WebSocket(wsEndpoint);

    ws.onopen = () => {
      setWsStatus('connected');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'sensor_update') {
        // Update historical chart data per device
        setDeviceData(prev => {
          const newData = { ...prev };
          data.readings.forEach(reading => {
            const id = reading.device_id;
            if (!newData[id]) newData[id] = [];
            
            // Keep last 20 readings for the chart
            newData[id] = [...newData[id], {
              time: new Date(reading.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}),
              voltage: reading.voltage,
              current: reading.current,
              temperature: reading.temperature,
              power_factor: reading.power_factor
            }].slice(-20);
          });
          return newData;
        });

        if (data.alerts && data.alerts.length > 0) {
          setAlerts(prev => [...data.alerts, ...prev].slice(0, 10)); // Keep top 10 alerts
        }
      }
    };

    ws.onerror = () => setWsStatus('error');
    ws.onclose = () => setWsStatus('disconnected');

    return () => ws.close();
  }, []);

  const triggerDemo = async (scenario) => {
    try {
      await fetchApi(endpoints.demoScenarioActivate, {
        method: 'POST',
        body: JSON.stringify({ scenario })
      });
      alert(`Scenario ${scenario} activated! Watch the charts.`);
    } catch (err) {
      alert('Failed to trigger scenario');
    }
  };

  const renderKPIs = () => (
    <div className="kpi-grid">
      <div className="glass-card kpi-card">
        <div className="kpi-icon primary"><Activity size={24} /></div>
        <div className="kpi-info">
          <span className="text-muted text-sm">Monitored Devices</span>
          <h3 className="text-xl font-bold">{stats?.total_devices || 4}</h3>
        </div>
      </div>
      <div className="glass-card kpi-card">
        <div className="kpi-icon warning"><AlertTriangle size={24} /></div>
        <div className="kpi-info">
          <span className="text-muted text-sm">Active Warnings</span>
          <h3 className="text-xl font-bold">{stats?.warning_devices || 0}</h3>
        </div>
      </div>
      <div className="glass-card kpi-card">
        <div className="kpi-icon critical"><ShieldAlert size={24} /></div>
        <div className="kpi-info">
          <span className="text-muted text-sm">Critical Alerts</span>
          <h3 className="text-xl font-bold">{alerts.filter(a => a.severity === 'CRITICAL').length}</h3>
        </div>
      </div>
      <div className="glass-card kpi-card demo-controls">
        <span className="text-muted text-sm mb-2 block">Demo Scenarios</span>
        <div className="flex gap-2">
          <button className="btn btn-outline text-sm" onClick={() => triggerDemo('overheating')}>Overheat</button>
          <button className="btn btn-outline text-sm" onClick={() => triggerDemo('short_circuit')}>Short Cct</button>
          <button className="btn btn-outline text-sm" onClick={() => triggerDemo('normal')}>Reset</button>
        </div>
      </div>
    </div>
  );

  return (
    <div className="dashboard-container animate-fade-in">
      <header className="page-header mb-6">
        <div>
          <h1 className="text-gradient">System Dashboard</h1>
          <p className="text-muted">Real-time IoT Sensor Monitoring</p>
        </div>
        <div className="flex items-center gap-2">
          <span className={`status-dot ${wsStatus === 'connected' ? 'online' : 'critical'}`}></span>
          <span className="text-sm">{wsStatus === 'connected' ? 'Live Stream Active' : 'Connecting...'}</span>
        </div>
      </header>

      {renderKPIs()}

      <div className="grid grid-cols-3 gap-6 mt-6">
        {/* Charts Section */}
        <div className="col-span-2 flex flex-col gap-6">
          {Object.keys(deviceData).map(deviceId => (
            <div key={deviceId} className="glass-panel p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-medium text-lg">{deviceId}</h3>
                <div className="flex gap-4">
                  <span className="text-sm text-primary flex items-center gap-1"><Zap size={14}/> Voltage</span>
                  <span className="text-sm text-accent flex items-center gap-1"><Activity size={14}/> Current</span>
                  <span className="text-sm text-warning flex items-center gap-1"><Thermometer size={14}/> Temp</span>
                </div>
              </div>
              <div className="chart-container" style={{ height: '200px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={deviceData[deviceId]}>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                    <XAxis dataKey="time" stroke="rgba(255,255,255,0.3)" fontSize={12} tick={{fill: '#94a3b8'}} />
                    <YAxis stroke="rgba(255,255,255,0.3)" fontSize={12} tick={{fill: '#94a3b8'}} />
                    <Tooltip 
                      contentStyle={{ backgroundColor: 'rgba(24, 24, 27, 0.9)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                      itemStyle={{ color: '#fff' }}
                    />
                    <Line type="monotone" dataKey="voltage" stroke="var(--primary)" strokeWidth={2} dot={false} isAnimationActive={false} />
                    <Line type="monotone" dataKey="current" stroke="var(--accent)" strokeWidth={2} dot={false} isAnimationActive={false} />
                    <Line type="monotone" dataKey="temperature" stroke="var(--status-warning)" strokeWidth={2} dot={false} isAnimationActive={false} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          ))}
          {Object.keys(deviceData).length === 0 && (
            <div className="glass-panel p-6 flex justify-center items-center" style={{height: '300px'}}>
              <p className="text-muted">Waiting for sensor data...</p>
            </div>
          )}
        </div>

        {/* Alerts Sidebar */}
        <div className="alerts-section glass-panel p-6">
          <h3 className="font-medium text-lg mb-4 flex items-center gap-2">
            <AlertTriangle size={20} color="var(--status-warning)" />
            Recent Alerts
          </h3>
          <div className="alerts-list flex flex-col gap-3">
            {alerts.length === 0 ? (
              <p className="text-muted text-sm text-center mt-4">No recent alerts</p>
            ) : (
              alerts.map((alert, idx) => (
                <div key={idx} className={`alert-card ${alert.severity.toLowerCase()}`}>
                  <div className="flex justify-between items-start mb-1">
                    <span className="font-bold text-sm">{alert.device_id}</span>
                    <span className="text-xs opacity-70">{new Date(alert.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <h4 className="text-sm font-medium mb-1">{alert.title}</h4>
                  <p className="text-xs opacity-80">{alert.message}</p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
