import React from 'react';
import { PlaneTakeoff, PlaneLanding, AlertTriangle, ChevronRight, Clock } from 'lucide-react';

const FlightsView = () => {
  const flights = [
    {
      id: "LA 3314",
      route: "GRU → JFK",
      time: "Hoje, 22:45",
      status: "Risco Alto",
      statusColor: "#E11931",
      riskReason: "Overbooking (Densidade)",
      paxRisk: 14,
      costRisk: "R$ 35.000"
    },
    {
      id: "LA 8021",
      route: "CGH → SDU",
      time: "Amanhã, 06:15",
      status: "Risco Alto",
      statusColor: "#E11931",
      riskReason: "Hub Saturado (Clima)",
      paxRisk: 42,
      costRisk: "R$ 105.000"
    },
    {
      id: "LA 4502",
      route: "BSB → MIA",
      time: "Amanhã, 11:30",
      status: "Risco Médio",
      statusColor: "#FF9500", // Apple Orange
      riskReason: "Estouro de Jornada (Tripulação)",
      paxRisk: 120,
      costRisk: "R$ 300.000"
    },
    {
      id: "LA 3010",
      route: "CNF → GRU",
      time: "Amanhã, 14:00",
      status: "Normal",
      statusColor: "#34C759", // Apple Green
      riskReason: "-",
      paxRisk: 0,
      costRisk: "R$ 0"
    }
  ];

  return (
    <div className="flights-view slide-up" style={{ padding: '20px', paddingBottom: '100px', overflowY: 'auto', flex: 1 }}>
      <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '8px', color: '#1C1C1E' }}>
        Voos
      </h1>
      <p style={{ fontSize: '15px', color: '#8E8E93', marginBottom: '24px' }}>
        Monitoramento preditivo (24h)
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {flights.map((flight, idx) => (
          <div key={idx} className="flight-card" style={{ 
            backgroundColor: '#FFFFFF', 
            borderRadius: '16px', 
            padding: '16px', 
            boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05)',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px'
          }}>
            {/* Header: Flight Number & Status */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div style={{ backgroundColor: 'rgba(2, 0, 68, 0.05)', padding: '6px', borderRadius: '8px' }}>
                  <PlaneTakeoff size={18} color="#020044" />
                </div>
                <span style={{ fontWeight: '700', fontSize: '16px', color: '#1C1C1E' }}>{flight.id}</span>
              </div>
              <div style={{ 
                backgroundColor: `${flight.statusColor}15`, 
                color: flight.statusColor, 
                padding: '4px 10px', 
                borderRadius: '12px', 
                fontSize: '12px', 
                fontWeight: '600' 
              }}>
                {flight.status}
              </div>
            </div>

            {/* Route & Time */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
              <span style={{ fontSize: '18px', fontWeight: '600', color: '#020044', letterSpacing: '0.5px' }}>
                {flight.route}
              </span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#8E8E93' }}>
                <Clock size={14} />
                <span style={{ fontSize: '13px', fontWeight: '500' }}>{flight.time}</span>
              </div>
            </div>

            {/* Warning details (only if not normal) */}
            {flight.status !== "Normal" && (
              <div style={{ 
                backgroundColor: '#F2F2F7', 
                borderRadius: '12px', 
                padding: '12px', 
                marginTop: '4px',
                display: 'flex',
                flexDirection: 'column',
                gap: '8px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <AlertTriangle size={14} color={flight.statusColor} />
                  <span style={{ fontSize: '13px', color: '#1C1C1E', fontWeight: '500' }}>{flight.riskReason}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', borderTop: '1px solid #E5E5EA', paddingTop: '8px' }}>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontSize: '11px', color: '#8E8E93' }}>Pax em Risco</span>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: '#1C1C1E' }}>{flight.paxRisk}</span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
                    <span style={{ fontSize: '11px', color: '#8E8E93' }}>Exposição (BRL)</span>
                    <span style={{ fontSize: '14px', fontWeight: '600', color: '#E11931' }}>{flight.costRisk}</span>
                  </div>
                </div>
              </div>
            )}
            
            {flight.status !== "Normal" && (
              <button style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                paddingTop: '8px',
                borderTop: '1px solid #E5E5EA',
                marginTop: '4px',
                color: '#020044',
                fontWeight: '600',
                fontSize: '14px',
                width: '100%'
              }}>
                Resolver Anomalia
                <ChevronRight size={16} />
              </button>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default FlightsView;
