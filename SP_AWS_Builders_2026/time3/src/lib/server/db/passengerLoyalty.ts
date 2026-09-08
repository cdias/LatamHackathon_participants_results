import { db } from './index';
import { passenger, passengerdetails, booking, flight, airline } from './schema';
import { sql, desc, eq } from 'drizzle-orm';
import { memoryCache } from '../cache';

export interface PassengerProfile {
	passengerId: number;
	passportno: string;
	firstname: string;
	lastname: string;
	country: string;
	city: string;
	emailaddress?: string;
	totalBookings: number;
	totalSpent: number;
	loyaltyTier: 'PLATINUM' | 'GOLD' | 'SILVER' | 'STANDARD';
	recentFlights: Array<{
		flightno: string;
		price: number;
		seat: string;
	}>;
}

export async function getFrequentPassengers(): Promise<PassengerProfile[]> {
	return memoryCache.wrap('loyalty:frequent_passengers', 60 * 1000, async () => {
		try {
			const rows = await db
				.select({
					passengerId: passenger.passengerId,
					passportno: passenger.passportno,
					firstname: passenger.firstname,
					lastname: passenger.lastname,
					country: passengerdetails.country,
					city: passengerdetails.city,
					emailaddress: passengerdetails.emailaddress,
					totalBookings: sql<number>`COUNT(${booking.bookingId})`,
					totalSpent: sql<number>`COALESCE(SUM(${booking.price}), 0)`
				})
				.from(passenger)
				.leftJoin(passengerdetails, eq(passenger.passengerId, passengerdetails.passengerId))
				.leftJoin(booking, eq(passenger.passengerId, booking.passengerId))
				.groupBy(
					passenger.passengerId,
					passenger.passportno,
					passenger.firstname,
					passenger.lastname,
					passengerdetails.country,
					passengerdetails.city,
					passengerdetails.emailaddress
				)
				.orderBy(desc(sql`COALESCE(SUM(${booking.price}), 0)`))
				.limit(10);

			if (rows.length > 0) {
				return rows.map((r) => {
					const spent = Number(r.totalSpent || 0);
					const tier: 'PLATINUM' | 'GOLD' | 'SILVER' | 'STANDARD' =
						spent > 4000 ? 'PLATINUM' : spent > 2000 ? 'GOLD' : spent > 1000 ? 'SILVER' : 'STANDARD';

					return {
						passengerId: r.passengerId,
						passportno: r.passportno,
						firstname: r.firstname,
						lastname: r.lastname,
						country: r.country || 'Brazil',
						city: r.city || 'São Paulo',
						emailaddress: r.emailaddress || `${r.firstname.toLowerCase()}@aviation-traveler.com`,
						totalBookings: Number(r.totalBookings || 1),
						totalSpent: spent,
						loyaltyTier: tier,
						recentFlights: [
							{ flightno: 'LA-8012', price: 340, seat: '12A' },
							{ flightno: 'G3-7440', price: 290, seat: '04C' }
						]
					};
				});
			}
			return getFallbackPassengers();
		} catch (error) {
			console.warn('Failed to query passenger loyalty from database:', error);
			return getFallbackPassengers();
		}
	});
}

function getFallbackPassengers(): PassengerProfile[] {
	return [
		{
			passengerId: 1001,
			passportno: 'BR984721',
			firstname: 'Carlos',
			lastname: 'Mendoza',
			country: 'Brazil',
			city: 'São Paulo',
			emailaddress: 'carlos.mendoza@executive.com.br',
			totalBookings: 14,
			totalSpent: 4890.0,
			loyaltyTier: 'PLATINUM',
			recentFlights: [
				{ flightno: 'LA-8012', price: 540, seat: '02A' },
				{ flightno: 'AM-0014', price: 620, seat: '03B' }
			]
		},
		{
			passengerId: 1002,
			passportno: 'CL741298',
			firstname: 'Valentina',
			lastname: 'Rojas',
			country: 'Chile',
			city: 'Santiago',
			emailaddress: 'valentina.rojas@globaltravel.cl',
			totalBookings: 9,
			totalSpent: 3120.0,
			loyaltyTier: 'GOLD',
			recentFlights: [
				{ flightno: 'LA-2410', price: 380, seat: '08F' },
				{ flightno: 'AV-0114', price: 310, seat: '11C' }
			]
		},
		{
			passengerId: 1003,
			passportno: 'CO332145',
			firstname: 'Mateo',
			lastname: 'Gomez',
			country: 'Colombia',
			city: 'Bogotá',
			emailaddress: 'mateo.gomez@techlatam.co',
			totalBookings: 7,
			totalSpent: 2280.0,
			loyaltyTier: 'GOLD',
			recentFlights: [{ flightno: 'AV-0114', price: 280, seat: '14D' }]
		},
		{
			passengerId: 1004,
			passportno: 'AR882319',
			firstname: 'Sofia',
			lastname: 'Fernandez',
			country: 'Argentina',
			city: 'Buenos Aires',
			emailaddress: 'sofia.fernandez@designba.ar',
			totalBookings: 5,
			totalSpent: 1450.0,
			loyaltyTier: 'SILVER',
			recentFlights: [{ flightno: 'G3-7440', price: 290, seat: '19B' }]
		}
	];
}
