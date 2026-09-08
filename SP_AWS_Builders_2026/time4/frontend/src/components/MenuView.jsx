import React from 'react';
import { User, Database, MessageCircle, Settings, FileText, LogOut, ChevronRight, Brain } from 'lucide-react';

const MenuView = () => {
  const menuGroups = [
    {
      title: "Conta",
      items: [
        { icon: <User size={20} color="#020044" />, label: "Perfil do Gestor" }
      ]
    },
    {
      title: "Integrações",
      items: [
        { icon: <Database size={20} color="#34C759" />, label: "TiDB Cloud (Airport DB)" },
        { icon: <MessageCircle size={20} color="#34C759" />, label: "WhatsApp API (Passageiros)" }
      ]
    },
    {
      title: "Inteligência Artificial",
      items: [
        { icon: <Brain size={20} color="#9C27B0" />, label: "Swarm Models (Claude 3.5)" },
        { icon: <FileText size={20} color="#FF9500" />, label: "Playbooks de Regras" }
      ]
    },
    {
      title: "Sistema",
      items: [
        { icon: <Settings size={20} color="#8E8E93" />, label: "Ajustes do Aplicativo" },
        { icon: <LogOut size={20} color="#E11931" />, label: "Sair", hideChevron: true, textColor: "#E11931" }
      ]
    }
  ];

  return (
    <div className="menu-view slide-up" style={{ padding: '20px', paddingBottom: '100px', overflowY: 'auto', flex: 1, backgroundColor: '#F2F2F7' }}>
      <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '24px', color: '#1C1C1E' }}>
        Menu
      </h1>

      {menuGroups.map((group, groupIdx) => (
        <div key={groupIdx} style={{ marginBottom: '24px' }}>
          <h2 style={{ fontSize: '13px', textTransform: 'uppercase', color: '#8E8E93', fontWeight: '600', marginBottom: '8px', paddingLeft: '16px' }}>
            {group.title}
          </h2>
          <div style={{ 
            backgroundColor: '#FFFFFF', 
            borderRadius: '16px', 
            overflow: 'hidden'
          }}>
            {group.items.map((item, itemIdx) => (
              <div key={itemIdx}>
                <button style={{ 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'space-between', 
                  width: '100%', 
                  padding: '16px',
                  backgroundColor: 'transparent'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                    <div style={{ 
                      width: '32px', 
                      height: '32px', 
                      borderRadius: '8px', 
                      backgroundColor: 'rgba(242, 242, 247, 0.8)', 
                      display: 'flex', 
                      alignItems: 'center', 
                      justifyContent: 'center' 
                    }}>
                      {item.icon}
                    </div>
                    <span style={{ fontSize: '16px', fontWeight: '500', color: item.textColor || '#1C1C1E' }}>
                      {item.label}
                    </span>
                  </div>
                  {!item.hideChevron && <ChevronRight size={20} color="#C7C7CC" />}
                </button>
                
                {/* Divider below item unless it's the last item in the group */}
                {itemIdx < group.items.length - 1 && (
                  <div style={{ height: '1px', backgroundColor: '#E5E5EA', marginLeft: '64px' }}></div>
                )}
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

export default MenuView;
