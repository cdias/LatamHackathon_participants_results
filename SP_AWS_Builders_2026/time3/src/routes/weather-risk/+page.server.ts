import type { PageServerLoad } from './$types';
import { getRecentWeatherData, getFlightsAtRisk } from '$lib/server/db/weatherRisk';
import { generateWeatherBriefing } from '$lib/server/ai/weatherRiskAdvisor';

export const load: PageServerLoad = async () => {
	const [stations, flights, aiBriefing] = await Promise.all([
		getRecentWeatherData(),
		getFlightsAtRisk(),
		generateWeatherBriefing()
	]);

	return {
		stations,
		flights,
		briefing: aiBriefing.briefing,
		isFallback: aiBriefing.isFallback
	};
};
