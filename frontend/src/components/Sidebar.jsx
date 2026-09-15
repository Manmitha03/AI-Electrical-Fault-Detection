import React from 'react';
import { NavLink } from 'react-router-dom';
import { Activity, Camera, MessageSquare, ShieldAlert } from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-icon">
          <ShieldAlert size={28} color="var(--primary)" />
        </div>
        <div className="logo-text">
          <h2 className="text-gradient">VoltGuard AI</h2>
          <span className="text-xs text-muted">Intelligent Diagnostics</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        <NavLink to="/" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'} end>
          <Activity size={20} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/diagnostics" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          <Activity size={20} />
          <span>Diagnostics</span>
        </NavLink>
        <NavLink to="/ar-guidance" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          <Camera size={20} />
          <span>AR Guidance</span>
        </NavLink>
        <NavLink to="/chatbot" className={({isActive}) => isActive ? 'nav-item active' : 'nav-item'}>
          <MessageSquare size={20} />
          <span>AI Assistant</span>
        </NavLink>
      </nav>

      <div className="sidebar-footer">
        <div className="status-indicator">
          <span className="status-dot online"></span>
          <span className="text-sm">System Online</span>
        </div>
        <p className="text-xs text-muted mt-2" style={{opacity: 0.6}}>
          Interview Demo Mode Active
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
