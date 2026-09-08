import React, { useState, useEffect } from 'react';
import { X, CheckCircle, Loader2, Server, DollarSign, BookOpen, Shield, Cpu } from 'lucide-react';

const SwarmSimulator = ({ isOpen, onClose }) => {
  const [selectedScenario, setSelectedScenario] = useState("Overbooking em Voo de Alta Densidade");
  const [isSimulating, setIsSimulating] = useState(false);
  const [logs, setLogs] = useState([]);
  const [isComplete, setIsComplete] = useState(false);

  // Simulation steps matching Streamlit's logic
  const steps = [
    { id: 1, icon: <Server size={18} color="#8E8E93" />, text: "COST RADAR: Varrendo airportdb no TiDB Cloud...", delay: 1000 },
    { id: 2, icon: <AlertIcon />, text: `Identificado: {scenario} (Ação nas próximas 24h).`, delay: 2000 },
    { id: 3, icon: <DollarSign size={18} color="#8E8E93" />, text: "PRICING & RISK: Calculando Matriz Financeira...", delay: 3000 },
    { id: 4, icon: <DollarSign size={18} color="#E11931" />, text: "-> Involuntário: Multa ANAC + Hotel + Danos Morais = R$ 2.500/pax", delay: 4000 },
    { id: 5, icon: <DollarSign size={18} color="#34C759" />, text: "-> Voluntário (Pré-Check-in): Voucher Reacomodação = R$ 300/pax", delay: 4500 },
    { id: 6, icon: <BookOpen size={18} color="#8E8E93" />, text: "PLAYBOOK AGENT: Buscando vetor VECTOR(1024) no TiDB...", delay: 5500 },
    { id: 7, icon: <BookOpen size={18} color="#007AFF" />, text: "-> Encontrado Playbook Recomendado para o cenário!", delay: 6500 },
    { id: 8, icon: <Shield size={18} color="#8E8E93" />, text: "DEVIL'S ADVOCATE: Validando plano com SQL Relacional...", delay: 7500 },
    { id: 9, icon: <Shield size={18} color="#34C759" />, text: "-> Disponibilidade confirmada para voos alternativos 2h depois.", delay: 8500 },
    { id: 10, icon: <Cpu size={18} color="#020044" />, text: "DECIDER / STRATEGIST: Orquestração Final (Claude 3.5 Sonnet)", delay: 9500 },
    { id: 11, icon: <CheckCircle size={18} color="#34C759" />, text: "-> Plano Aprovado. Disparando API do WhatsApp para os 1.420 passageiros.", delay: 10500 },
    { id: 12, icon: <CheckCircle size={18} color="#34C759" />, text: "-> Audit Trail gravado em decision_log.", delay: 11000 },
  ];

  const handleStart = () => {
    setIsSimulating(true);
    setLogs([]);
    setIsComplete(false);
  };

  useEffect(() => {
    if (isSimulating) {
      let timeoutIds = [];
      
      steps.forEach((step, index) => {
        const id = setTimeout(() => {
          setLogs(prev => [...prev, {
            ...step,
            text: step.text.replace('{scenario}', selectedScenario)
          }]);
          
          if (index === steps.length - 1) {
            setIsComplete(true);
          }
        }, step.delay);
        timeoutIds.push(id);
      });

      return () => timeoutIds.forEach(clearTimeout);
    }
  }, [isSimulating, selectedScenario]);

  const handleClose = () => {
    // Reset state on close
    setIsSimulating(false);
    setLogs([]);
    setIsComplete(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay fade-in">
      <div className="bottom-sheet slide-up">
        <div className="sheet-header">
          <div className="drag-indicator"></div>
          <h3 className="sheet-title">Simular Cenário</h3>
          <button className="close-btn" onClick={handleClose}>
            <X size={24} color="#8E8E93" />
          </button>
        </div>

        <div className="sheet-content">
          {!isSimulating ? (
            <div className="setup-view fade-in">
              <label className="input-label">Selecione o risco operacional:</label>
              <div className="radio-group">
                {[
                  "Overbooking em Voo de Alta Densidade", 
                  "Conexão de Alto Risco em Hub Saturado", 
                  "Risco de Estouro de Jornada da Tripulação"
                ].map((scenario) => (
                  <button 
                    key={scenario}
                    className={`radio-option ${selectedScenario === scenario ? 'selected' : ''}`}
                    onClick={() => setSelectedScenario(scenario)}
                  >
                    <div className="radio-circle">
                      {selectedScenario === scenario && <div className="radio-dot"></div>}
                    </div>
                    <span>{scenario}</span>
                  </button>
                ))}
              </div>

              <button className="primary-btn mt-24" onClick={handleStart}>
                Acionar Swarm IA
              </button>
            </div>
          ) : (
            <div className="simulation-view fade-in">
              <div className="logs-container">
                {logs.map((log, index) => (
                  <div key={index} className="log-entry slide-up" style={{ animationDuration: '0.3s' }}>
                    <div className="log-icon">{log.icon}</div>
                    <div className="log-text">{log.text}</div>
                  </div>
                ))}
                
                {!isComplete && (
                  <div className="log-entry loading">
                    <Loader2 size={18} color="#020044" className="spinner" />
                    <span className="log-text italic">Processando...</span>
                  </div>
                )}
              </div>

              {isComplete && (
                <div className="success-banner fade-in">
                  <CheckCircle size={24} color="#34C759" />
                  <div className="success-info">
                    <h4>Resolução Completa!</h4>
                    <p>Prejuízo evitado: ~R$ 3.1M. Ações gravadas via API.</p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Simple alert icon helper
const AlertIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#E11931" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/>
  </svg>
);

export default SwarmSimulator;
