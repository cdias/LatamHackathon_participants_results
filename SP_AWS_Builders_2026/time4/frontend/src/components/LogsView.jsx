import React from 'react';
import { FileCheck, ShieldCheck, CheckCircle2, ChevronRight } from 'lucide-react';

const LogsView = () => {
  const auditLogs = [
    {
      id: "LOG-9281",
      date: "Hoje, 14:32",
      scenario: "Overbooking (Densidade)",
      decision: "Reacomodação Voluntária",
      savings: "+ R$ 3.1M",
      status: "Aprovado",
    },
    {
      id: "LOG-9280",
      date: "Ontem, 09:15",
      scenario: "Conexão de Risco",
      decision: "Voo Alternativo (Parceira)",
      savings: "+ R$ 850K",
      status: "Aprovado",
    },
    {
      id: "LOG-9279",
      date: "01 Set, 22:10",
      scenario: "Estouro de Jornada",
      decision: "Troca de Tripulação (Base GRU)",
      savings: "+ R$ 1.2M",
      status: "Aprovado",
    },
    {
      id: "LOG-9278",
      date: "31 Ago, 18:45",
      scenario: "Manutenção Não Programada",
      decision: "Upgrade Equipamento (777)",
      savings: "+ R$ 420K",
      status: "Aprovado",
    }
  ];

  return (
    <div className="logs-view slide-up" style={{ padding: '20px', paddingBottom: '100px', overflowY: 'auto', flex: 1, backgroundColor: '#F2F2F7' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', color: '#1C1C1E' }}>
          Extrato
        </h1>
        <div style={{ backgroundColor: 'rgba(52, 199, 89, 0.15)', padding: '6px 12px', borderRadius: '16px', display: 'flex', alignItems: 'center', gap: '6px' }}>
          <ShieldCheck size={16} color="#127236" />
          <span style={{ fontSize: '12px', fontWeight: '600', color: '#127236' }}>Compliance Ativo</span>
        </div>
      </div>
      
      <p style={{ fontSize: '15px', color: '#8E8E93', marginBottom: '24px' }}>
        Logs estruturados de decisões da IA.
      </p>

      <div style={{ backgroundColor: '#FFFFFF', borderRadius: '16px', overflow: 'hidden', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.03)' }}>
        {auditLogs.map((log, idx) => (
          <div key={idx} style={{ 
            display: 'flex', 
            padding: '16px', 
            borderBottom: idx < auditLogs.length - 1 ? '1px solid #E5E5EA' : 'none',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flex: 1 }}>
              <div style={{ 
                width: '40px', 
                height: '40px', 
                borderRadius: '50%', 
                backgroundColor: 'rgba(2, 0, 68, 0.05)', 
                display: 'flex', 
                alignItems: 'center', 
                justifyContent: 'center',
                flexShrink: 0
              }}>
                <FileCheck size={20} color="#020044" />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', overflow: 'hidden' }}>
                <span style={{ fontSize: '15px', fontWeight: '600', color: '#1C1C1E', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {log.scenario}
                </span>
                <span style={{ fontSize: '13px', color: '#8E8E93' }}>
                  {log.date} • {log.decision}
                </span>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', marginLeft: '12px' }}>
              <span style={{ fontSize: '15px', fontWeight: '700', color: '#34C759' }}>
                {log.savings}
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', marginTop: '4px' }}>
                <CheckCircle2 size={12} color="#8E8E93" />
                <span style={{ fontSize: '11px', color: '#8E8E93' }}>{log.status}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <button style={{
        marginTop: '24px',
        width: '100%',
        padding: '16px',
        backgroundColor: '#FFFFFF',
        borderRadius: '12px',
        color: '#020044',
        fontWeight: '600',
        fontSize: '15px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '8px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.02)'
      }}>
        Exportar Relatório ANAC
        <ChevronRight size={18} color="#C7C7CC" />
      </button>
    </div>
  );
};

export default LogsView;
