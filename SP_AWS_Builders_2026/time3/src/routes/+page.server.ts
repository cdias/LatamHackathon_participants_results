import type { PageServerLoad } from './$types';
import {
	getDashboardKPIs,
	getRevenueAndBookingTrends,
	getTopRoutes,
	getAirlinePerformance,
	getFleetUtilization,
	getPassengerDemographics,
	getWeeklyScheduleDistribution,
	getAllAirportsAndAirlines
} from '$lib/server/db/analytics';

export const load: PageServerLoad = async () => {
	const [kpis, trends, topRoutes, airlines, fleet, demographics, weeklySchedule, meta] =
		await Promise.all([
			getDashboardKPIs(),
			getRevenueAndBookingTrends(),
			getTopRoutes(8),
			getAirlinePerformance(),
			getFleetUtilization(),
			getPassengerDemographics(),
			getWeeklyScheduleDistribution(),
			getAllAirportsAndAirlines()
		]);

	return {
		kpis,
		trends,
		topRoutes,
		airlines,
		fleet,
		demographics,
		weeklySchedule,
		meta
	};
};
