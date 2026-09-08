import {
	mysqlTable,
	mysqlSchema,
	type AnyMySqlColumn,
	index,
	foreignKey,
	smallint,
	tinyint,
	char,
	varchar,
	int,
	mediumint,
	text,
	decimal,
	date,
	mysqlEnum,
	datetime,
	time
} from "drizzle-orm/mysql-core";
import { sql } from "drizzle-orm";


export const airline = mysqlTable("airline", {
	airlineId: smallint("airline_id").autoincrement().notNull(),
	iata: char({ length: 2 }).notNull(),
	airlinename: varchar({ length: 30 }),
	baseAirport: smallint("base_airport").notNull().references(() => airport.airportId),
},
(table) => [
	index("iata_unq").on(table.iata),
	index("base_airport_idx").on(table.baseAirport),
]);

export const airplane = mysqlTable("airplane", {
	airplaneId: int("airplane_id").autoincrement().notNull(),
	capacity: mediumint({ unsigned: true }).notNull(),
	typeId: int("type_id").notNull().references(() => airplaneType.typeId),
	airlineId: int("airline_id").notNull(),
},
(table) => [
	index("type_id").on(table.typeId),
]);

export const airplaneType = mysqlTable("airplane_type", {
	typeId: int("type_id").autoincrement().notNull(),
	identifier: varchar({ length: 50 }),
	description: text(),
});

export const airport = mysqlTable("airport", {
	airportId: smallint("airport_id").autoincrement().notNull(),
	iata: char({ length: 3 }),
	icao: char({ length: 4 }).notNull(),
	name: varchar({ length: 50 }).notNull(),
},
(table) => [
	index("icao_unq").on(table.icao),
	index("name_idx").on(table.name),
	index("iata_idx").on(table.iata),
]);

export const airportGeo = mysqlTable("airport_geo", {
	airportId: smallint("airport_id").notNull().references(() => airport.airportId),
	name: varchar({ length: 50 }).notNull(),
	city: varchar({ length: 50 }),
	country: varchar({ length: 50 }),
	latitude: decimal({ precision: 11, scale: 8 }).notNull(),
	longitude: decimal({ precision: 11, scale: 8 }).notNull(),
});

export const booking = mysqlTable("booking", {
	bookingId: int("booking_id").autoincrement().notNull(),
	flightId: int("flight_id").notNull().references(() => flight.flightId),
	seat: char({ length: 4 }),
	passengerId: int("passenger_id").notNull().references(() => passenger.passengerId),
	price: decimal({ precision: 10, scale: 2 }).notNull(),
},
(table) => [
	index("seatplan_unq").on(table.flightId, table.seat),
	index("flight_idx").on(table.flightId),
	index("passenger_idx").on(table.passengerId),
]);

export const employee = mysqlTable("employee", {
	employeeId: int("employee_id").autoincrement().notNull(),
	firstname: varchar({ length: 100 }).notNull(),
	lastname: varchar({ length: 100 }).notNull(),
	// you can use { mode: 'date' }, if you want to have Date as type for this column
	birthdate: date({ mode: 'string' }).notNull(),
	sex: char({ length: 1 }),
	street: varchar({ length: 100 }).notNull(),
	city: varchar({ length: 100 }).notNull(),
	zip: smallint().notNull(),
	country: varchar({ length: 100 }).notNull(),
	emailaddress: varchar({ length: 120 }),
	telephoneno: varchar({ length: 30 }),
	salary: decimal({ precision: 8, scale: 2 }),
	department: mysqlEnum(['Marketing','Accounting','Management','Logistics','Airfield']),
	username: varchar({ length: 20 }),
	password: char({ length: 32 }),
},
(table) => [
	index("user_unq").on(table.username),
]);

export const flight = mysqlTable("flight", {
	flightId: int("flight_id").autoincrement().notNull(),
	flightno: char({ length: 8 }).notNull().references(() => flightschedule.flightno),
	from: smallint().notNull().references(() => airport.airportId),
	to: smallint().notNull().references(() => airport.airportId),
	departure: datetime({ mode: 'string'}).notNull(),
	arrival: datetime({ mode: 'string'}).notNull(),
	airlineId: smallint("airline_id").notNull().references(() => airline.airlineId),
	airplaneId: int("airplane_id").notNull().references(() => airplane.airplaneId),
},
(table) => [
	index("from_idx").on(table.from),
	index("to_idx").on(table.to),
	index("departure_idx").on(table.departure),
	index("arrivals_idx").on(table.arrival),
	index("airline_idx").on(table.airlineId),
	index("airplane_idx").on(table.airplaneId),
	index("flightno").on(table.flightno),
]);

export const flightschedule = mysqlTable("flightschedule", {
	flightno: char({ length: 8 }).notNull(),
	from: smallint().notNull().references(() => airport.airportId),
	to: smallint().notNull().references(() => airport.airportId),
	departure: time().notNull(),
	arrival: time().notNull(),
	airlineId: smallint("airline_id").notNull().references(() => airline.airlineId),
	monday: tinyint().default(0),
	tuesday: tinyint().default(0),
	wednesday: tinyint().default(0),
	thursday: tinyint().default(0),
	friday: tinyint().default(0),
	saturday: tinyint().default(0),
	sunday: tinyint().default(0),
},
(table) => [
	index("from_idx").on(table.from),
	index("to_idx").on(table.to),
	index("airline_idx").on(table.airlineId),
]);

export const passenger = mysqlTable("passenger", {
	passengerId: int("passenger_id").autoincrement().notNull(),
	passportno: char({ length: 9 }).notNull(),
	firstname: varchar({ length: 100 }).notNull(),
	lastname: varchar({ length: 100 }).notNull(),
},
(table) => [
	index("pass_unq").on(table.passportno),
]);

export const passengerdetails = mysqlTable("passengerdetails", {
	passengerId: int("passenger_id").notNull().references(() => passenger.passengerId, { onDelete: "cascade" } ),
	// you can use { mode: 'date' }, if you want to have Date as type for this column
	birthdate: date({ mode: 'string' }).notNull(),
	sex: char({ length: 1 }),
	street: varchar({ length: 100 }).notNull(),
	city: varchar({ length: 100 }).notNull(),
	zip: smallint().notNull(),
	country: varchar({ length: 100 }).notNull(),
	emailaddress: varchar({ length: 120 }),
	telephoneno: varchar({ length: 30 }),
});

export const weatherdata = mysqlTable("weatherdata", {
	// you can use { mode: 'date' }, if you want to have Date as type for this column
	logDate: date("log_date", { mode: 'string' }).notNull(),
	time: time().notNull(),
	station: int().notNull(),
	temp: decimal({ precision: 3, scale: 1 }).notNull(),
	humidity: decimal({ precision: 4, scale: 1 }).notNull(),
	airpressure: decimal({ precision: 10, scale: 2 }).notNull(),
	wind: decimal({ precision: 5, scale: 2 }).notNull(),
	weather: mysqlEnum(['fog-snowfall','snowfall','rain','rain-snowfall','fog-rain','fog-rain-thunderstorm','thunderstorm','fog','rain-thunderstorm']),
	winddirection: smallint().notNull(),
});
