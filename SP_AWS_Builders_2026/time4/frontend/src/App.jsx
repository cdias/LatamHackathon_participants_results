import React, { useState } from 'react';
import './App.css';
import Header from './components/Header';
import { 
  ChevronRight, 
  ExternalLink,
  Home,
  Plane,
  Tag,
  FileText,
  Menu,
  Activity,
  Zap,
  ShieldCheck,
  RefreshCw
} from 'lucide-react';
import SwarmSimulator from './components/SwarmSimulator';
import FlightsView from './components/FlightsView';
import MenuView from './components/MenuView';
import LogsView from './components/LogsView';

function App() {
  const [activeTab, setActiveTab] = useState('home');
  const [isSimulatorOpen, setIsSimulatorOpen] = useState(false);

  return (
    <>
      <Header />
      
      {activeTab === 'home' && (
        <div className="main-content slide-up" style={{ animationDelay: '0.1s' }}>
          
          {/* Promo Card -> AI Swarm Trigger */}
          <div className="promo-card" onClick={() => setIsSimulatorOpen(true)} style={{ cursor: 'pointer' }}>
            <div className="promo-info">
              <span className="promo-title">
                <Zap size={18} color="#020044" />
                Acionar Swarm IA
              </span>
              <span className="promo-desc">
                Resolva anomalias em tempo real e minimize prejuízos.
              </span>
            </div>
            <button className="promo-btn">
              <ChevronRight size={20} color="#8E8E93" />
            </button>
          </div>

          {/* Section Title */}
          <h2 className="section-title">Maximize sua eficiência hoje</h2>
          <p className="section-subtitle">Ações recomendadas para as próximas 24h.</p>

          {/* Action Grid */}
          <div className="action-grid">
            <button className="action-card" onClick={() => setIsSimulatorOpen(true)}>
              <Activity size={24} className="action-icon" />
              <ExternalLink size={16} className="action-icon-corner" />
              <span className="action-label">Simular<br/>Cenários</span>
            </button>
            
            <button className="action-card">
              <ShieldCheck size={24} className="action-icon" />
              <ChevronRight size={16} className="action-icon-corner" />
              <span className="action-label">Auditoria<br/>ANAC</span>
            </button>

            <button className="action-card">
              <RefreshCw size={24} className="action-icon" />
              <ChevronRight size={16} className="action-icon-corner" />
              <span className="action-label">Sincronizar<br/>TiDB</span>
            </button>

            <button className="action-card">
              <FileText size={24} className="action-icon" />
              <ExternalLink size={16} className="action-icon-corner" />
              <span className="action-label">Relatórios<br/>de Risco</span>
            </button>
          </div>
        </div>
      )}

      {activeTab === 'viagens' && <FlightsView />}
      
      {activeTab === 'extrato' && <LogsView />}
      
      {activeTab === 'menu' && <MenuView />}
      
      {/* Bottom Navigation */}
      <div className="bottom-nav">
        <button 
          className={`nav-item ${activeTab === 'home' ? 'active' : ''}`}
          onClick={() => setActiveTab('home')}
        >
          <Home size={24} />
          <span className="nav-label">Home</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'viagens' ? 'active' : ''}`}
          onClick={() => setActiveTab('viagens')}
        >
          <Plane size={24} />
          <span className="nav-label">Voos</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'market' ? 'active' : ''}`}
          onClick={() => setActiveTab('market')}
        >
          <Tag size={24} />
          <span className="nav-label">Decisões</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'extrato' ? 'active' : ''}`}
          onClick={() => setActiveTab('extrato')}
        >
          <FileText size={24} />
          <span className="nav-label">Logs</span>
        </button>
        <button 
          className={`nav-item ${activeTab === 'menu' ? 'active' : ''}`}
          onClick={() => setActiveTab('menu')}
        >
          <Menu size={24} />
          <span className="nav-label">Menu</span>
        </button>
      </div>

      <SwarmSimulator 
        isOpen={isSimulatorOpen} 
        onClose={() => setIsSimulatorOpen(false)} 
      />
    </>
  );
}

export default App;
