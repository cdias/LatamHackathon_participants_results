-- Current sql file was generated after introspecting the database
-- If you want to run this migration please uncomment this code before executing migrations
/*
CREATE TABLE `airline` (
	`airline_id` smallint AUTO_INCREMENT NOT NULL,
	`iata` char(2) NOT NULL,
	`airlinename` varchar(30),
	`base_airport` smallint NOT NULL
);
--> statement-breakpoint
CREATE TABLE `airplane` (
	`airplane_id` int AUTO_INCREMENT NOT NULL,
	`capacity` mediumint unsigned NOT NULL,
	`type_id` int NOT NULL,
	`airline_id` int NOT NULL
);
--> statement-breakpoint
CREATE TABLE `airplane_type` (
	`type_id` int AUTO_INCREMENT NOT NULL,
	`identifier` varchar(50),
	`description` text
);
--> statement-breakpoint
CREATE TABLE `airport` (
	`airport_id` smallint AUTO_INCREMENT NOT NULL,
	`iata` char(3),
	`icao` char(4) NOT NULL,
	`name` varchar(50) NOT NULL
);
--> statement-breakpoint
CREATE TABLE `airport_geo` (
	`airport_id` smallint NOT NULL,
	`name` varchar(50) NOT NULL,
	`city` varchar(50),
	`country` varchar(50),
	`latitude` decimal(11,8) NOT NULL,
	`longitude` decimal(11,8) NOT NULL
);
--> statement-breakpoint
CREATE TABLE `booking` (
	`booking_id` int AUTO_INCREMENT NOT NULL,
	`flight_id` int NOT NULL,
	`seat` char(4),
	`passenger_id` int NOT NULL,
	`price` decimal(10,2) NOT NULL
);
--> statement-breakpoint
CREATE TABLE `employee` (
	`employee_id` int AUTO_INCREMENT NOT NULL,
	`firstname` varchar(100) NOT NULL,
	`lastname` varchar(100) NOT NULL,
	`birthdate` date NOT NULL,
	`sex` char(1),
	`street` varchar(100) NOT NULL,
	`city` varchar(100) NOT NULL,
	`zip` smallint NOT NULL,
	`country` varchar(100) NOT NULL,
	`emailaddress` varchar(120),
	`telephoneno` varchar(30),
	`salary` decimal(8,2),
	`department` enum('Marketing','Accounting','Management','Logistics','Airfield'),
	`username` varchar(20),
	`password` char(32)
);
--> statement-breakpoint
CREATE TABLE `flight` (
	`flight_id` int AUTO_INCREMENT NOT NULL,
	`flightno` char(8) NOT NULL,
	`from` smallint NOT NULL,
	`to` smallint NOT NULL,
	`departure` datetime NOT NULL,
	`arrival` datetime NOT NULL,
	`airline_id` smallint NOT NULL,
	`airplane_id` int NOT NULL
);
--> statement-breakpoint
CREATE TABLE `flightschedule` (
	`flightno` char(8) NOT NULL,
	`from` smallint NOT NULL,
	`to` smallint NOT NULL,
	`departure` time NOT NULL,
	`arrival` time NOT NULL,
	`airline_id` smallint NOT NULL,
	`monday` tinyint(1) DEFAULT 0,
	`tuesday` tinyint(1) DEFAULT 0,
	`wednesday` tinyint(1) DEFAULT 0,
	`thursday` tinyint(1) DEFAULT 0,
	`friday` tinyint(1) DEFAULT 0,
	`saturday` tinyint(1) DEFAULT 0,
	`sunday` tinyint(1) DEFAULT 0
);
--> statement-breakpoint
CREATE TABLE `passenger` (
	`passenger_id` int AUTO_INCREMENT NOT NULL,
	`passportno` char(9) NOT NULL,
	`firstname` varchar(100) NOT NULL,
	`lastname` varchar(100) NOT NULL
);
--> statement-breakpoint
CREATE TABLE `passengerdetails` (
	`passenger_id` int NOT NULL,
	`birthdate` date NOT NULL,
	`sex` char(1),
	`street` varchar(100) NOT NULL,
	`city` varchar(100) NOT NULL,
	`zip` smallint NOT NULL,
	`country` varchar(100) NOT NULL,
	`emailaddress` varchar(120),
	`telephoneno` varchar(30)
);
--> statement-breakpoint
CREATE TABLE `weatherdata` (
	`log_date` date NOT NULL,
	`time` time NOT NULL,
	`station` int NOT NULL,
	`temp` decimal(3,1) NOT NULL,
	`humidity` decimal(4,1) NOT NULL,
	`airpressure` decimal(10,2) NOT NULL,
	`wind` decimal(5,2) NOT NULL,
	`weather` enum('fog-snowfall','snowfall','rain','rain-snowfall','fog-rain','fog-rain-thunderstorm','thunderstorm','fog','rain-thunderstorm'),
	`winddirection` smallint NOT NULL
);
--> statement-breakpoint
ALTER TABLE `airline` ADD CONSTRAINT `airline_ibfk_1` FOREIGN KEY (`base_airport`) REFERENCES `airport`(`airport_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `airplane` ADD CONSTRAINT `airplane_ibfk_1` FOREIGN KEY (`type_id`) REFERENCES `airplane_type`(`type_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `airport_geo` ADD CONSTRAINT `airport_geo_ibfk_1` FOREIGN KEY (`airport_id`) REFERENCES `airport`(`airport_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `booking` ADD CONSTRAINT `booking_ibfk_1` FOREIGN KEY (`flight_id`) REFERENCES `flight`(`flight_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `booking` ADD CONSTRAINT `booking_ibfk_2` FOREIGN KEY (`passenger_id`) REFERENCES `passenger`(`passenger_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `flight` ADD CONSTRAINT `flight_ibfk_1` FOREIGN KEY (`from`) REFERENCES `airport`(`airport_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `flight` ADD CONSTRAINT `flight_ibfk_2` FOREIGN KEY (`to`) REFERENCES `airport`(`airport_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `flight` ADD CONSTRAINT `flight_ibfk_3` FOREIGN KEY (`airline_id`) REFERENCES `airline`(`airline_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `flight` ADD CONSTRAINT `flight_ibfk_4` FOREIGN KEY (`airplane_id`) REFERENCES `airplane`(`airplane_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `flight` ADD CONSTRAINT `flight_ibfk_5` FOREIGN KEY (`flightno`) REFERENCES `flightschedule`(`flightno`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `flightschedule` ADD CONSTRAINT `flightschedule_ibfk_1` FOREIGN KEY (`from`) REFERENCES `airport`(`airport_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `flightschedule` ADD CONSTRAINT `flightschedule_ibfk_2` FOREIGN KEY (`to`) REFERENCES `airport`(`airport_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `flightschedule` ADD CONSTRAINT `flightschedule_ibfk_3` FOREIGN KEY (`airline_id`) REFERENCES `airline`(`airline_id`) ON DELETE no action ON UPDATE no action;--> statement-breakpoint
ALTER TABLE `passengerdetails` ADD CONSTRAINT `passengerdetails_ibfk_1` FOREIGN KEY (`passenger_id`) REFERENCES `passenger`(`passenger_id`) ON DELETE cascade ON UPDATE no action;--> statement-breakpoint
CREATE INDEX `iata_unq` ON `airline` (`iata`);--> statement-breakpoint
CREATE INDEX `base_airport_idx` ON `airline` (`base_airport`);--> statement-breakpoint
CREATE INDEX `type_id` ON `airplane` (`type_id`);--> statement-breakpoint
CREATE INDEX `icao_unq` ON `airport` (`icao`);--> statement-breakpoint
CREATE INDEX `name_idx` ON `airport` (`name`);--> statement-breakpoint
CREATE INDEX `iata_idx` ON `airport` (`iata`);--> statement-breakpoint
CREATE INDEX `seatplan_unq` ON `booking` (`flight_id`,`seat`);--> statement-breakpoint
CREATE INDEX `flight_idx` ON `booking` (`flight_id`);--> statement-breakpoint
CREATE INDEX `passenger_idx` ON `booking` (`passenger_id`);--> statement-breakpoint
CREATE INDEX `user_unq` ON `employee` (`username`);--> statement-breakpoint
CREATE INDEX `from_idx` ON `flight` (`from`);--> statement-breakpoint
CREATE INDEX `to_idx` ON `flight` (`to`);--> statement-breakpoint
CREATE INDEX `departure_idx` ON `flight` (`departure`);--> statement-breakpoint
CREATE INDEX `arrivals_idx` ON `flight` (`arrival`);--> statement-breakpoint
CREATE INDEX `airline_idx` ON `flight` (`airline_id`);--> statement-breakpoint
CREATE INDEX `airplane_idx` ON `flight` (`airplane_id`);--> statement-breakpoint
CREATE INDEX `flightno` ON `flight` (`flightno`);--> statement-breakpoint
CREATE INDEX `from_idx` ON `flightschedule` (`from`);--> statement-breakpoint
CREATE INDEX `to_idx` ON `flightschedule` (`to`);--> statement-breakpoint
CREATE INDEX `airline_idx` ON `flightschedule` (`airline_id`);--> statement-breakpoint
CREATE INDEX `pass_unq` ON `passenger` (`passportno`);
*/