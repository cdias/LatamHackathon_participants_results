import React from 'react';
import { X, BellRing, AlertTriangle, Info, CheckCircle } from 'lucide-react';

const NotificationsModal = ({ isOpen, onClose }) => {
  const notifications = [
    {
      id: 1,
      type: 'alert',
      title: 'Risco Alto Detectado',
      message: 'Voo LA 3314 com 14 pax em overbooking.',
      time: 'Há 5 min'
    },
    {
      id: 2,
      type: 'success',
      title: 'Swarm IA Finalizado',
      message: 'Economia de R$ 3.1M gerada no hub de GRU.',
      time: 'Há 22 min'
    },
    {
      id: 3,
      type: 'info',
      title: 'Atualização ANAC',
      message: 'Novas diretrizes de acomodação publicadas.',
      time: 'Há 1 hora'
    }
  ];

  if (!isOpen) return null;

  const getIcon = (type) => {
    switch(type) {
      case 'alert': return <AlertTriangle size={18} color="#E11931" />;
      case 'success': return <CheckCircle size={18} color="#34C759" />;
      case 'info': return <Info size={18} color="#007AFF" />;
      default: return <BellRing size={18} color="#020044" />;
    }
  };

  return (
    <div className="modal-overlay fade-in">
      <div className="drawer-right slide-in-right">
        <div className="sheet-header" style={{ alignItems: 'flex-start' }}>
          <h3 className="sheet-title">Notificações</h3>
          <button className="close-btn" onClick={onClose} style={{ top: '-10px', right: '0' }}>
            <X size={24} color="#8E8E93" />
          </button>
        </div>

        <div className="sheet-content">
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {notifications.map((notif) => (
              <div key={notif.id} style={{ 
                display: 'flex', 
                gap: '12px', 
                backgroundColor: '#FFFFFF',
                padding: '16px',
                borderRadius: '16px',
                border: '1px solid #E5E5EA'
              }}>
                <div style={{ 
                  width: '36px', 
                  height: '36px', 
                  borderRadius: '50%', 
                  backgroundColor: 'rgba(2, 0, 68, 0.04)', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  flexShrink: 0
                }}>
                  {getIcon(notif.type)}
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <span style={{ fontSize: '15px', fontWeight: '600', color: '#1C1C1E' }}>{notif.title}</span>
                    <span style={{ fontSize: '11px', color: '#8E8E93' }}>{notif.time}</span>
                  </div>
                  <span style={{ fontSize: '13px', color: '#3A3A3C', lineHeight: '1.4' }}>{notif.message}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default NotificationsModal;
