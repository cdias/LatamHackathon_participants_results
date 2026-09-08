import React, { useState } from 'react';
import { Bell, ShieldAlert, AlertTriangle, TrendingDown } from 'lucide-react';
import NotificationsModal from './NotificationsModal';

const Header = () => {
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  return (
    <div className="header-container slide-up">
      <div className="header-top">
        <div className="logo-area">
          <img src="/logo.png" alt="Revenue Guard" className="logo-img" />
        </div>
        <button className="bell-btn" onClick={() => setIsNotifOpen(true)}>
          <Bell color="#FFFFFF" size={20} />
          <span className="badge">3</span>
        </button>
      </div>
      
      <h1 className="greeting">Olá, GESTOR</h1>
      
      <div className="top-cards-container">
        <div className="top-card">
          <div className="top-card-icon bg-red">
            <AlertTriangle color="#FFFFFF" size={20} />
          </div>
          <div className="top-card-info">
            <span className="top-card-label">Voos em Alerta</span>
            <span className="top-card-value">47</span>
          </div>
        </div>
        
        <div className="top-card">
          <div className="top-card-icon bg-navy">
            <TrendingDown color="#FFFFFF" size={20} />
          </div>
          <div className="top-card-info">
            <span className="top-card-label">Risco Previsto</span>
            <span className="top-card-value">R$ 3.5M</span>
          </div>
        </div>

        <div className="top-card">
          <div className="top-card-icon" style={{ backgroundColor: '#34C759' }}>
            <TrendingDown color="#FFFFFF" size={20} style={{ transform: 'rotate(180deg)' }} />
          </div>
          <div className="top-card-info">
            <span className="top-card-label">Economia Swarm</span>
            <span className="top-card-value">R$ 3.1M</span>
          </div>
        </div>
      </div>
      
      <div className="carousel-dots">
        <div className="dot active"></div>
        <div className="dot"></div>
        <div className="dot"></div>
      </div>

      <NotificationsModal 
        isOpen={isNotifOpen}
        onClose={() => setIsNotifOpen(false)}
      />
    </div>
  );
};

export default Header;
