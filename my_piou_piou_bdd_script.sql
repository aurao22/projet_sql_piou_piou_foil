DROP TABLE IF EXISTS mesure;
DROP TABLE IF EXISTS station;

CREATE TABLE station (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	station_name TEXT NOT NULL,
	latitude REAL,
	longitude REAL
);


CREATE TABLE mesure (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	mesure_date TEXT NOT NULL,
	wind_heading REAL,
	wind_speed_avg REAL,
	wind_speed_max REAL,
    wind_speed_min REAL,
	station INTEGER,
	FOREIGN KEY(station) references station(id)
);

SELECT * FROM station;