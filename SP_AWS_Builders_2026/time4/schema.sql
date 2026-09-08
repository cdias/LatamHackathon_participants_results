-- 1. Memória Vetorial de Playbooks Financeiros e Operacionais
CREATE TABLE IF NOT EXISTS disruption_playbook (
id BIGINT AUTO_RANDOM PRIMARY KEY,
scenario TEXT NOT NULL,
internal_action TEXT NOT NULL,
financial_impact_voluntario INT NOT NULL,
financial_impact_involuntario INT NOT NULL,
embedding VECTOR(1024) GENERATED ALWAYS AS
(EMBED_TEXT('tidbcloud_free/amazon/titan-embed-text-v2', scenario)) STORED
);

-- 2. Log de Auditoria Regulatória (Compliance ANAC / Prova Jurídica)
CREATE TABLE IF NOT EXISTS decision_log (
id BIGINT AUTO_RANDOM PRIMARY KEY,
disruption_scenario TEXT NOT NULL,
cost_radar_analysis JSON NOT NULL,
pricing_classification JSON NOT NULL,
devil_objections JSON NOT NULL,
final_decision JSON NOT NULL,
estimated_savings_brl DECIMAL(10,2) NOT NULL,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Inserção de Playbooks de Exemplo
INSERT INTO disruption_playbook
(scenario, internal_action, financial_impact_voluntario, financial_impact_involuntario)
VALUES
('overbooking em voo de alta densidade', 'ofertar voucher de R$ 350 para voo 2h depois', 350, 2500),
('conexao de alto risco em hub saturado', 'reacomodar voluntariamente via app 24h antes', 300, 2200),
('risco de estouro de jornada de tripulacao', 'troca preventiva de equipe ou cancelamento programado', 500, 5000);
