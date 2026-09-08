import { json, type RequestHandler } from '@sveltejs/kit';
import { generateWeatherBriefing } from '$lib/server/ai/weatherRiskAdvisor';
import { getRecentWeatherData, getFlightsAtRisk } from '$lib/server/db/weatherRisk';

export const GET: RequestHandler = async () => {
	const [stations, flights, aiBriefing] = await Promise.all([
		getRecentWeatherData(),
		getFlightsAtRisk(),
		generateWeatherBriefing()
	]);

	return json({
		stations,
		flights,
		briefing: aiBriefing.briefing,
		isFallback: aiBriefing.isFallback
	});
};
