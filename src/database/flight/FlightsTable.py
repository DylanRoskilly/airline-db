from typing import Iterator
from database.flight.Flight import Flight, ExtendedFlight
from database.Table import Table, Column
from database.validation import validate_date_time
from cli.TextTable import TextTable

class FlightsTable(Table):
    def __init__(self, database):
        super().__init__(database)
        
        self.columns = {
            "Flight ID": Column(
                name="flights.flight_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.exists(x),
                validation_prompt="A flight's ID must be a non negative integer and must exist in the database"
            ),
            "Aircraft ID": Column(
                name="flights.aircraft_id", 
                settable=True, 
                insert_prompt="What's the ID of the aircraft for this flight?", 
                update_prompt="What's the ID of the new aircraft for this flight?", 
                is_valid=lambda x : x.isdigit() and self.db.aircrafts.exists(x),
                validation_prompt="An aircraft's ID must be a non negative integer and must exist in the database"
            ),
            "Terminal ID": Column(
                name="flights.terminal_id", 
                settable=True,
                insert_prompt="What's the ID of the terminal for this flight?",
                update_prompt="What's the ID of the new terminal for this flight?",
                is_valid=lambda x : x.isdigit() and self.db.terminals.exists(x),
                validation_prompt="An terminals's ID must be a non negative integer and must exist in the database"
            ),
            "Destination": Column(
                name="destination", 
                settable=True,
                insert_prompt="What's the destination of this flight?",
                update_prompt="What's the new destination of this flight?",
                is_valid=lambda x : 0 < len(x) <= 100,
                validation_prompt="A flight's destination must be between 1 and 100 characters inclusive"
            ),
            "Boarding Time": Column(
                name="boarding_time", 
                settable=True,
                insert_prompt="What's the boarding time of this flight in YYYY-MM-DD HH:MM:SS format?",
                update_prompt="What's the new boarding time of this flight in YYYY-MM-DD HH:MM:SS format?",
                is_valid=validate_date_time, 
                validation_prompt="A flight's boarding time must be in the format YYYY-MM-DD HH:MM:SS"
            ),
            "Departure Time": Column(
                name="departure_time", 
                settable=True,
                insert_prompt="What's the departure time of this flight in YYYY-MM-DD HH:MM:SS format?",
                update_prompt="What's the new departure time of this flight in YYYY-MM-DD HH:MM:SS format?",
                is_valid=validate_date_time, 
                validation_prompt="A flight's departure time must be in the format YYYY-MM-DD HH:MM:SS"
            ),
            "Arrival Time": Column(
                name="arrival_time", 
                settable=True,
                insert_prompt="What's the arrival time of this flight in YYYY-MM-DD HH:MM:SS format?",
                update_prompt="What's the new arrival time of this flight in YYYY-MM-DD HH:MM:SS format?",
                is_valid=validate_date_time,
                validation_prompt="A flight's arrival time must be in the format YYYY-MM-DD HH:MM:SS"
            )
        }

    def create_table(self) -> None:
        try:
            self.db.cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS flights (
                        flight_id INTEGER PRIMARY KEY,
                        aircraft_id INTEGER NOT NULL,
                        terminal_id INTEGER NOT NULL,
                        destination VARCHAR(100) NOT NULL,
                        boarding_time VARCHAR(19) NOT NULL,
                        departure_time VARCHAR(19) NOT NULL,
                        arrival_time VARCHAR(19) NOT NULL,

                        FOREIGN KEY (aircraft_id) REFERENCES aircrafts ON DELETE CASCADE,
                        FOREIGN KEY (terminal_id) REFERENCES terminals ON DELETE CASCADE
                    );
                """
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to create flights table")

    # values = (aircraft_id, terminal_id, destination, boarding_time, departure_time, arrival_time)
    def insert(self, values: tuple[str]) -> Flight:
        try:
            self.db.cursor.execute(
                """
                    INSERT INTO flights 
                    VALUES (NULL, ?, ?, ?, ?, ?, ?)
                    RETURNING flight_id;
                """,
                values
            )

            flight = Flight(self.db.cursor.fetchone()[0], *values)  

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to insert into flights table")
        else:
            return flight

    def update(self, flight_id: int, column_name: str, new_value: str) -> Flight:
        try:
            self.db.cursor.execute(
                f"""
                    UPDATE flights 
                    SET {column_name} = ?
                    WHERE flight_id = ?
                    RETURNING *;
                """,
                (new_value, flight_id)
            )

            flight = Flight(*self.db.cursor.fetchone())  

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to update flights table")
        else:
            return flight
    
    def get_all(self) -> Iterator[ExtendedFlight]:
        try:
            self.db.cursor.execute(
                """
                    SELECT flight_id, flights.aircraft_id, aircrafts.name, flights.terminal_id, airports.name, terminals.name, destination, boarding_time, departure_time, arrival_time
                    FROM flights
                    JOIN aircrafts ON flights.aircraft_id = aircrafts.aircraft_id
                    JOIN terminals ON flights.terminal_id = terminals.terminal_id
                    JOIN airports ON terminals.airport_id = airports.airport_id;
                """
            )
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get all rows from flights table")
        else:
            return map(lambda row : ExtendedFlight(*row), rows) 

    def get(self, column_name: str, value: str) -> Iterator[ExtendedFlight]:
        try:
            self.db.cursor.execute(
                f"""
                    SELECT flights.flight_id, flights.aircraft_id, aircrafts.name, flights.terminal_id, airports.name, terminals.name, destination, boarding_time, departure_time, arrival_time
                    FROM flights
                    JOIN aircrafts ON flights.aircraft_id = aircrafts.aircraft_id
                    JOIN terminals ON flights.terminal_id = terminals.terminal_id
                    JOIN airports ON terminals.airport_id = airports.airport_id
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get rows based on a column in flights table")
        else:
            return map(lambda row : ExtendedFlight(*row), rows)  

    def delete_and_return(self, column_name: str, value: str) -> Iterator[Flight]:
        try:
            self.db.cursor.execute(
                f"""
                    DELETE FROM flights
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            self.db.connection.commit()

            self.db.cursor.execute("SELECT * FROM flights;")
            remaining_rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to delete from flights table")
        else:
            return map(lambda row : Flight(*row), remaining_rows) 

    def exists(self, flight_id: int) -> bool:
        try:
            self.db.cursor.execute(
                """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM flights 
                        WHERE flight_id = ?
                    );
                """,
                (flight_id,)
            )
            exists = self.db.cursor.fetchone()[0]
        except:
            self.db.handle_error("Unable to determine if flight exists")
        else:
            return False if exists == 0 else True