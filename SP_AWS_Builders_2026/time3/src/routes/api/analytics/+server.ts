import { json, type RequestHandler } from '@sveltejs/kit';
import {
	getDashboardKPIs,
	getRevenueAndBookingTrends,
	getTopRoutes,
	getAirlinePerformance,
	getFleetUtilization,
	getPassengerDemographics,
	getWeeklyScheduleDistribution,
	getAllAirportsAndAirlines,
	type AnalyticsFilter
} from '$lib/server/db/analytics';

export const GET: RequestHandler = async ({ url }) => {
	const airlineId = url.searchParams.get('airlineId') ? Number(url.searchParams.get('airlineId')) : undefined;
	const fromAirportId = url.searchParams.get('fromAirportId') ? Number(url.searchParams.get('fromAirportId')) : undefined;

	const filter: AnalyticsFilter = { airlineId, fromAirportId };

	const [kpis, trends, topRoutes, airlines, fleet, demographics, weeklySchedule, meta] = await Promise.all([
		getDashboardKPIs(filter),
		getRevenueAndBookingTrends(filter),
		getTopRoutes(8, filter),
		getAirlinePerformance(filter),
		getFleetUtilization(filter),
		getPassengerDemographics(filter),
		getWeeklyScheduleDistribution(filter),
		getAllAirportsAndAirlines()
	]);

	return json({
		kpis,
		trends,
		topRoutes,
		airlines,
		fleet,
		demographics,
		weeklySchedule,
		meta
	});
};
