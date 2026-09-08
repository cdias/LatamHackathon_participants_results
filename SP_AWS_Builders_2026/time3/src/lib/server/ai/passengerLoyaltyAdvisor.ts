import { invokeBedrock } from './bedrock';
import type { PassengerProfile } from '../db/passengerLoyalty';

export interface RebookingProposal {
	passengerName: string;
	loyaltyTier: string;
	proposalSummary: string;
	alternativeFlights: Array<{
		flightno: string;
		route: string;
		timeDifference: string;
		seatUpgrade: string;
	}>;
	compensationPackage: string;
	personalizedMessage: string;
	isFallback?: boolean;
}

export async function generateRebookingOffer(
	passenger: PassengerProfile,
	disruptedFlightno = 'LA-8012',
	language: 'pt' | 'es' | 'en' = 'pt'
): Promise<RebookingProposal> {
	const prompt = `
Gere uma Proposta Inteligente de Reacomodação e Recuperação de Fidelidade VIP para um passageiro afetado por atraso/cancelamento de voo.

Perfil do Passageiro:
- Nome: ${passenger.firstname} ${passenger.lastname}
- Categoria de Fidelidade: ${passenger.loyaltyTier}
- Valor Total Investido: $${passenger.totalSpent}
- Cidade/País de Origem: ${passenger.city}, ${passenger.country}
- Voo Impactado: ${disruptedFlightno}
- Idioma de Destino: ${language}

Forneça uma resposta estruturada em markdown no idioma selecionado (${language}):
1. **Estratégia de Retenção VIP**: Ação personalizada para a categoria (${passenger.loyaltyTier}).
2. **Itinerário Alternativo Recomendado**: 2 melhores conexões alternativas com upgrade de assento.
3. **Pacote de Compensação e Bônus**: Crédito em milhas, voucher e acesso ao Lounge VIP.
4. **Minuta de Comunicação Personalizada (em ${language})**: Mensagem atenciosa e proativa pronta para envio via WhatsApp/E-mail.
`;

	const systemPrompt = 'Você é um agente executivo de atendimento e fidelidade VIP para companhias aéreas internacionais.';
	const res = await invokeBedrock(prompt, systemPrompt);

	return {
		passengerName: `${passenger.firstname} ${passenger.lastname}`,
		loyaltyTier: passenger.loyaltyTier,
		proposalSummary: res.text,
		alternativeFlights: [
			{ flightno: 'LA-8014', route: 'GRU → SCL', timeDifference: '+2h 15m', seatUpgrade: 'Premium Business 01C' },
			{ flightno: 'LA-8016', route: 'GRU → SCL', timeDifference: '+4h 30m', seatUpgrade: 'Premium Economy 03A' }
		],
		compensationPackage: passenger.loyaltyTier === 'PLATINUM' ? 'Voucher de $150 + 10.000 Milhas Bônus + Acesso ao VIP Lounge' : 'Voucher de $75 + 5.000 Milhas Bônus',
		personalizedMessage: res.text,
		isFallback: res.isFallback
	};
}
