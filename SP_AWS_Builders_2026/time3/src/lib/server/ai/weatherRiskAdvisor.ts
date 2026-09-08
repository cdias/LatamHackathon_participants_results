import { invokeBedrock } from './bedrock';
import { getRecentWeatherData, getFlightsAtRisk } from '../db/weatherRisk';

export async function generateWeatherBriefing(): Promise<{ briefing: string; isFallback?: boolean }> {
	const [stations, flights] = await Promise.all([
		getRecentWeatherData(),
		getFlightsAtRisk()
	]);

	const prompt = `
Você é o Chefe de Despacho Operacional de Voo e IA Meteorológica para uma aliança aérea latino-americana no TiDB.
Aqui está o relatório de telemetria das estações meteorológicas em tempo real e partidas programadas impactadas:

Telemetria das Estações:
${JSON.stringify(stations, null, 2)}

Voos Programados em Risco:
${JSON.stringify(flights, null, 2)}

Forneça um Briefing Tático Operacional de Clima em markdown formatado em Português Brasileiro contendo:
1. **Pontos Críticos de Atenção Meteorológica**: Resumo de tempestades convectivas, rajadas de vento e baixa visibilidade nos principais hubs (GRU, GIG, EZE, SCL, BOG).
2. **Plano de Mitigação Operacional de Voo**: Instruções táticas de contingência de combustível (+45 min), esperas em solo e procedimentos CAT II.
3. **Protocolo de Atendimento ao Passageiro**: Orientações para equipes de solo e portão de embarque.
`;

	const systemPrompt = 'Você é um especialista em operações aéreas e meteorologia aeronáutica fornecendo briefings táticos concisos e executivos em português.';

	const res = await invokeBedrock(prompt, systemPrompt);

	return {
		briefing: res.text,
		isFallback: res.isFallback
	};
}
