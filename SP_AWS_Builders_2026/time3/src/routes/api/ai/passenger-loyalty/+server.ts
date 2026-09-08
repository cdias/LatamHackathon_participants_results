import { json, type RequestHandler } from '@sveltejs/kit';
import { generateRebookingOffer } from '$lib/server/ai/passengerLoyaltyAdvisor';
import { getFrequentPassengers } from '$lib/server/db/passengerLoyalty';

export const POST: RequestHandler = async ({ request }) => {
	try {
		const { passengerId, language = 'en' } = await request.json();
		const passengers = await getFrequentPassengers();
		const targetPassenger =
			passengers.find((p) => p.passengerId === Number(passengerId)) || passengers[0];

		if (!targetPassenger) {
			return json({ error: 'Passenger not found' }, { status: 404 });
		}

		const proposal = await generateRebookingOffer(
			targetPassenger,
			'LA-8012',
			language as 'pt' | 'es' | 'en'
		);

		return json({
			proposal,
			passengers
		});
	} catch (error) {
		console.error('Passenger loyalty API error:', error);
		return json({ error: 'Failed to generate loyalty proposal' }, { status: 500 });
	}
};
