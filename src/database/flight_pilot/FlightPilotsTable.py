from typing import Iterator
from database.flight_pilot.FlightPilot import FlightPilot 
from database.pilot.Pilot import Pilot 
from database.Table import Table, Column
from cli.TextTable import TextTable

class FlightPilotsTable(Table):
    def __init__(self, database):
        super().__init__(database)
        
        self.columns = { 
            "Flight ID": Column(
                name="flight_pilots.flight_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.db.flights.exists(x),
                validation_prompt="A flight's ID must be a non negative integer"
            ), 
            "Pilot ID": Column(
                name="flight_pilots.pilot_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.db.pilots.exists(x),
                validation_prompt="A pilot's ID must be a non negative integer"
            ),
        }

    def create_table(self) -> None:
        try:
            self.db.cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS flight_pilots (
                        flight_id INTEGER,
                        pilot_id INTEGER,

                        PRIMARY KEY (flight_id, pilot_id),
                        FOREIGN KEY (flight_id) REFERENCES flights ON DELETE CASCADE,
                        FOREIGN KEY (pilot_id) REFERENCES pilots ON DELETE CASCADE
                    );
                """
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to create flight pilots table")

    # add the pilot with id pilot_id to flight with id flight_id
    def insert(self, flight_id: int, pilot_id: int) -> FlightPilot:
        try:
            self.db.cursor.execute(
                """
                    INSERT INTO flight_pilots 
                    VALUES (?, ?);
                """,
                (flight_id, pilot_id)
            )

            flight_pilot = FlightPilot(flight_id, pilot_id)

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to insert into flight pilots table")
        else:
            return flight_pilot

    # returns all Pilots that are on the flight with id flight_id
    def get(self, flight_id: str) -> Iterator[Pilot]: 
        try:
            self.db.cursor.execute(
                """
                    SELECT pilots.pilot_id, first_name, last_name, date_of_birth
                    FROM flight_pilots
                    JOIN pilots ON pilots.pilot_id = flight_pilots.pilot_id
                    WHERE flight_id = ?;
                """, 
                (flight_id,)
            )
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get all pilots on flight")
        else:
            return map(lambda row : Pilot(*row), rows) 

    # removes pilot with id pilot_id from flight with id flight_id
    # returns the remainign Pilots on the flight
    def delete_and_return(self, flight_id: int, pilot_id: int) -> Iterator[Pilot]:
        try:
            self.db.cursor.execute(
                """
                    DELETE FROM flight_pilots
                    WHERE flight_id = ? AND pilot_id = ?;
                """,
                (flight_id, pilot_id)
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to delete from flight pilots table")
        else:
            return self.get(flight_id)
    
    # determines if the pilot is on the flight
    def exists(self, flight_id: int, pilot_id: int) -> bool:
        try:
            self.db.cursor.execute(
                """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM flight_pilots 
                        WHERE flight_id = ? AND pilot_id = ?
                    );
                """,
                (flight_id, pilot_id)
            )
            exists = self.db.cursor.fetchone()[0]
        except:
            self.db.handle_error("Unable to determine if pilot is on flight")
        else:
            return False if exists == 0 else True