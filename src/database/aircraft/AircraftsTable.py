from typing import Iterator
from database.aircraft.Aircraft import Aircraft 
from database.Table import Table, Column
from cli.TextTable import TextTable

class AircraftsTable(Table):
    def __init__(self, database):
        super().__init__(database)

        self.columns = {
            "Aircraft ID": Column(
                name="aircrafts.aircraft_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.exists(x),
                validation_prompt="An aircraft's ID must be a non negative integer and must exist in the database" 
            ),
            "Name": Column(
                name="name", 
                settable=True, 
                insert_prompt="What's the name of this aircraft?", 
                update_prompt="What's the new name of this aircraft?", 
                is_valid=lambda x : 0 < len(x) <= 50,
                validation_prompt="An aircraft's name must be between 1 and 50 characters inclusive"
            ),
            "Type": Column(
                name="type", 
                settable=True,
                insert_prompt="What type of aircraft is this?\n    1. Plane\n    2. Helicopter",
                update_prompt="What's the new type of this aircraft?\n    1. Plane\n    2. Helicopter",
                is_valid=lambda x : x == "1" or x == "2", 
                validation_prompt="An aircraft's type must be either 1 for plane or 2 for helicopter"
            ),
            "Max Passengers": Column(
                name="max_passengers", 
                settable=True,
                insert_prompt="What's the maximum number of passengers for this aircraft?",
                update_prompt="What's the new maximum number of passengers for this aircraft?",
                is_valid=lambda x : x.isdigit() and int(x) >= 1,
                validation_prompt="An aircraft's maximum number of passengers must be a positive integer"
            )
        }
    
    # creates the aircrafts table if it does not exist
    def create_table(self) -> None:
        try:
            self.db.cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS aircrafts (
                        aircraft_id INTEGER PRIMARY KEY,
                        name VARCHAR(50) NOT NULL,
                        type INTEGER NOT NULL,
                        max_passengers INTEGER NOT NULL
                    );
                """
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to create aircrafts table")

    # inserts the values into the aircrafts table and returns the inserted aircraft
    # the values parameter is a row. e.g. (name, type, max_passengers)
    def insert(self, values: tuple[str]) -> Aircraft:
        try:
            self.db.cursor.execute(
                """
                    INSERT INTO aircrafts 
                    VALUES (NULL, ?, ?, ?)
                    RETURNING aircraft_id;
                """,
                values
            )

            aircraft = Aircraft(self.db.cursor.fetchone()[0], *values) # create the new aircraft

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to insert into aircrafts table")
        else:
            return aircraft

    # updates column_name to new_value for a certain aircraft_id and returns the updated aircraft
    def update(self, aircraft_id: int, column_name: str, new_value: str) -> Aircraft:
        try:
            self.db.cursor.execute(
                f"""
                    UPDATE aircrafts 
                    SET {column_name} = ?
                    WHERE aircraft_id = ?
                    RETURNING *;
                """,
                (new_value, aircraft_id)
            )
            # the * operator is used to unpack the row tuple into parameters
            aircraft = Aircraft(*self.db.cursor.fetchone()) # create the updated aircraft

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to update aircrafts table")
        else:
            return aircraft
        
    # gets every aircraft in the table
    # this returns an iterator because map is used to convert all rows to aircrafts
    def get_all(self) -> Iterator[Aircraft]:
        try:
            self.db.cursor.execute("SELECT * FROM aircrafts;")
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get all rows in aircrafts table")
        else:
            return map(lambda row : Aircraft(*row), rows)

    # gets aircrafts whose column_name value is equal to value
    def get(self, column_name: str, value: str) -> Iterator[Aircraft]:
        try:
            self.db.cursor.execute(
                f"""
                    SELECT *
                    FROM aircrafts
                    WHERE {column_name} = ?;
                """,
                (value,) # trailing comma is required to create the tuple
            )
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get rows based on a column in aircrafts table")
        else:
            return map(lambda row : Aircraft(*row), rows)

    # deletes all aircrafts from the table whose column_name value equals value
    # returns the remaining aircrafts
    def delete_and_return(self, column_name: str, value: str) -> Iterator[Aircraft]:
        try:
            self.db.cursor.execute(
                f"""
                    DELETE FROM aircrafts
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to delete rows from aircrafts table")
        else:
            return self.get_all() # get remaining aircrafts

    # determines if an aircraft with aircraft_id exists in the table
    def exists(self, aircraft_id: int) -> bool:
        try:
            self.db.cursor.execute(
                """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM aircrafts 
                        WHERE aircraft_id = ?
                    );
                """,
                (aircraft_id,)
            )
            exists = self.db.cursor.fetchone()[0] 
        except:
            self.db.handle_error("Unable to determine if aircraft exists")
        else:
            return False if exists == 0 else True