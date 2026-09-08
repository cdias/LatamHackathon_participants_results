import streamlit as st
import pandas as pd
from core.db import run_query
import time

st.set_page_config(page_title="REVENUE GUARD | War Room", layout="wide")

st.title("🛡️ REVENUE GUARD")
st.subheader("Otimização Preditiva de Prejuízos Operacionais e Compliance ANAC")
st.markdown("---")

# 1. Cockpit Financeiro (KPIs)
st.header("📈 Cockpit Financeiro (Predição de 24h)")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Voos em Alerta (Próx 24h)", "47", "+12% vs ontem")
with col2:
    st.metric("Passageiros em Risco", "1.420", "-5% vs ontem")
with col3:
    st.metric("Risco Financeiro Potencial", "R$ 3.550.000", "Base R$2.500/pax")
with col4:
    st.metric("Economia Estimada (Midas)", "R$ 3.124.000", "Base R$300/pax")

st.markdown("---")

# 2. War Room do Swarm de IA
st.header("🤖 War Room - Swarm de IA em Ação")
st.markdown("Visualização ao vivo do debate entre os agentes e resolução preditiva.")

scenario_selected = st.selectbox(
    "Simular Cenário de Risco:", 
    ["Overbooking em Voo de Alta Densidade", "Conexão de Alto Risco em Hub Saturado", "Risco de Estouro de Jornada da Tripulação"]
)

if st.button("Acionar Swarm (Insight Midas)"):
    with st.status("Executando Swarm de IA...", expanded=True) as status:
        st.write("🔍 **COST RADAR**: Varrendo `airportdb` no TiDB Cloud...")
        time.sleep(1)
        st.write(f"⚠️ Identificado: {scenario_selected} (Ação nas próximas 24h).")
        
        st.write("🧮 **PRICING & RISK**: Calculando Matriz Financeira...")
        time.sleep(1)
        st.write("-> Involuntário: Multa ANAC + Hotel + Danos Morais = R$ 2.500/pax")
        st.write("-> Voluntário (Pré-Check-in): Voucher Reacomodação = R$ 300/pax")

        st.write("📚 **PLAYBOOK AGENT**: Buscando vetor `VECTOR(1024)` no TiDB...")
        time.sleep(1)
        try:
            # Tenta ler a regra vetorial diretamente do banco (para simular a infra)
            playbooks = run_query("SELECT scenario, internal_action, financial_impact_voluntario FROM disruption_playbook LIMIT 3")
            if not playbooks.empty:
                st.write("-> Encontrado Playbook Recomendado para o cenário!")
                st.dataframe(playbooks, use_container_width=True)
            else:
                st.write("-> Base de playbooks vazia. (Rode o schema.sql para popular)")
        except:
            st.write("-> Simulação de Vector Search (Banco não populado).")

        st.write("👿 **DEVIL'S ADVOCATE**: Validando plano com SQL Relacional (Contra-Queries)...")
        time.sleep(1)
        st.write("-> Disponibilidade confirmada para voos alternativos 2h depois.")
        
        st.write("🎯 **DECIDER / STRATEGIST**: Orquestração Final (Claude 3.5 Sonnet)")
        time.sleep(1)
        st.write("-> Plano Aprovado. Disparando API do WhatsApp para os 1.420 passageiros.")
        st.write("-> Audit Trail gravado em `decision_log`.")
        
        status.update(label="Resolução Completa!", state="complete", expanded=False)
    
    st.success(f"🚀 Mensagens enviadas com sucesso! Prejuízo evitado: ~R$ 3.1M.")

st.markdown("---")
st.header("📋 Audit Trail (Compliance ANAC)")
st.info("Logs estruturados salvos no TiDB Cloud para prova jurídica de assistência.")
try:
    logs = run_query("SELECT id, disruption_scenario, final_decision, estimated_savings_brl, created_at FROM decision_log ORDER BY id DESC LIMIT 5")
    if not logs.empty:
        st.dataframe(logs, use_container_width=True)
    else:
        st.write("Nenhum log de decisão registrado ainda.")
except:
    st.write("Banco de dados ainda não configurado para logs.")
