from typing import Iterator
from database.airport.Airport import Airport 
from database.Table import Table, Column
from cli.TextTable import TextTable

class AirportsTable(Table):
    def __init__(self, database):
        super().__init__(database)
        
        self.columns = {
            "Airport ID": Column(
                name="airports.airport_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.exists(x),
                validation_prompt="An airport's ID must be a non negative integer and must exist in the database"
            ),
            "Name": Column(
                name="name", 
                settable=True, 
                insert_prompt="What's the name of this airport?", 
                update_prompt="What's the new name of this airport?", 
                is_valid=lambda x : 0 < len(x) <= 100,
                validation_prompt="An airport's name must be between 1 and 100 characters inclusive"
            ),
            "Address": Column(
                name="address", 
                settable=True,
                insert_prompt="What's the address of this airport?",
                update_prompt="What's the new address of this aircraft?",
                is_valid=lambda x : len(x) > 1, 
                validation_prompt="An airport's address must be more than 1 character"
            )
        }

    def create_table(self) -> None:
        try:
            self.db.cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS airports (
                        airport_id INTEGER PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        address TEXT NOT NULL
                    );
                """
            )

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to create airports table")

    # values = (name, address)
    def insert(self, values: tuple[str]) -> Airport:
        try:
            self.db.cursor.execute(
                """
                    INSERT INTO airports 
                    VALUES (NULL, ?, ?)
                    RETURNING airport_id;
                """,
                values
            )

            airport = Airport(self.db.cursor.fetchone()[0], *values)  

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to insert into airports table")
        else:
            return airport

    def update(self, airport_id: int, column_name: str, new_value: str) -> Airport:
        try:
            self.db.cursor.execute(
                f"""
                    UPDATE airports 
                    SET {column_name} = ?
                    WHERE airport_id = ?
                    RETURNING *;
                """,
                (new_value, airport_id)
            )

            airport = Airport(*self.db.cursor.fetchone())  

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to update airports table")
        else:
            return airport

    def get_all(self) -> Iterator[Airport]:
        try:
            self.db.cursor.execute("SELECT * FROM airports;")
            rows = self.db.cursor.fetchall()
        except:
            self.handle_error("Unable to get all rows from airports table")
        else:
            return map(lambda row : Airport(*row), rows)

    def get(self, column_name: str, value: str) -> Iterator[Airport]:
        try:
            self.db.cursor.execute(
                f"""
                    SELECT *
                    FROM airports
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get rows based on a column in airports table")
        else:
            return map(lambda row : Airport(*row), rows)

    def delete_and_return(self, column_name: str, value: str) -> Iterator[Airport]:
        try:
            self.db.cursor.execute(
                f"""
                    DELETE FROM airports
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to delete from airports table")
        else:
            return self.get_all()

    def exists(self, airport_id: int) -> bool:
        try:
            self.db.cursor.execute(
                """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM airports 
                        WHERE airport_id = ?
                    );
                """,
                (airport_id,)
            )
            exists = self.db.cursor.fetchone()[0]
        except:
            self.db.handle_error("Unable to determine if airport exists")
        else:
            return False if exists == 0 else True