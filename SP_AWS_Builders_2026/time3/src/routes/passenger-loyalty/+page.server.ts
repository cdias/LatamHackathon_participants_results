import type { PageServerLoad } from './$types';
import { getFrequentPassengers } from '$lib/server/db/passengerLoyalty';
import { generateRebookingOffer } from '$lib/server/ai/passengerLoyaltyAdvisor';

export const load: PageServerLoad = async () => {
	const passengers = await getFrequentPassengers();
	const initialProposal = await generateRebookingOffer(
		passengers[0],
		'LA-8012',
		'en'
	);

	return {
		passengers,
		initialProposal
	};
};
