import { relations } from "drizzle-orm/relations";
import { airport, airline, airplaneType, airplane, airportGeo, flight, booking, passenger, flightschedule, passengerdetails } from "./schema";

export const airlineRelations = relations(airline, ({one, many}) => ({
	airport: one(airport, {
		fields: [airline.baseAirport],
		references: [airport.airportId]
	}),
	flights: many(flight),
	flightschedules: many(flightschedule),
}));

export const airportRelations = relations(airport, ({many}) => ({
	airlines: many(airline),
	airportGeos: many(airportGeo),
	flights_from: many(flight, {
		relationName: "flight_from_airport_airportId"
	}),
	flights_to: many(flight, {
		relationName: "flight_to_airport_airportId"
	}),
	flightschedules_from: many(flightschedule, {
		relationName: "flightschedule_from_airport_airportId"
	}),
	flightschedules_to: many(flightschedule, {
		relationName: "flightschedule_to_airport_airportId"
	}),
}));

export const airplaneRelations = relations(airplane, ({one, many}) => ({
	airplaneType: one(airplaneType, {
		fields: [airplane.typeId],
		references: [airplaneType.typeId]
	}),
	flights: many(flight),
}));

export const airplaneTypeRelations = relations(airplaneType, ({many}) => ({
	airplanes: many(airplane),
}));

export const airportGeoRelations = relations(airportGeo, ({one}) => ({
	airport: one(airport, {
		fields: [airportGeo.airportId],
		references: [airport.airportId]
	}),
}));

export const bookingRelations = relations(booking, ({one}) => ({
	flight: one(flight, {
		fields: [booking.flightId],
		references: [flight.flightId]
	}),
	passenger: one(passenger, {
		fields: [booking.passengerId],
		references: [passenger.passengerId]
	}),
}));

export const flightRelations = relations(flight, ({one, many}) => ({
	bookings: many(booking),
	airport_from: one(airport, {
		fields: [flight.from],
		references: [airport.airportId],
		relationName: "flight_from_airport_airportId"
	}),
	airport_to: one(airport, {
		fields: [flight.to],
		references: [airport.airportId],
		relationName: "flight_to_airport_airportId"
	}),
	airline: one(airline, {
		fields: [flight.airlineId],
		references: [airline.airlineId]
	}),
	airplane: one(airplane, {
		fields: [flight.airplaneId],
		references: [airplane.airplaneId]
	}),
	flightschedule: one(flightschedule, {
		fields: [flight.flightno],
		references: [flightschedule.flightno]
	}),
}));

export const passengerRelations = relations(passenger, ({many}) => ({
	bookings: many(booking),
	passengerdetails: many(passengerdetails),
}));

export const flightscheduleRelations = relations(flightschedule, ({one, many}) => ({
	flights: many(flight),
	airport_from: one(airport, {
		fields: [flightschedule.from],
		references: [airport.airportId],
		relationName: "flightschedule_from_airport_airportId"
	}),
	airport_to: one(airport, {
		fields: [flightschedule.to],
		references: [airport.airportId],
		relationName: "flightschedule_to_airport_airportId"
	}),
	airline: one(airline, {
		fields: [flightschedule.airlineId],
		references: [airline.airlineId]
	}),
}));

export const passengerdetailsRelations = relations(passengerdetails, ({one}) => ({
	passenger: one(passenger, {
		fields: [passengerdetails.passengerId],
		references: [passenger.passengerId]
	}),
}));