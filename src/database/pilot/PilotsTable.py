from typing import Iterable
from database.pilot.Pilot import Pilot 
from database.Table import Table, Column
from database.validation import validate_date
from cli.TextTable import TextTable

class PilotsTable(Table):
    def __init__(self, database):
        super().__init__(database)
        
        self.columns = { 
            "Pilot ID": Column(
                name="pilots.pilot_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.exists(x),
                validation_prompt="A pilot's ID must be a non negative integer and must exist in the database"
            ),
            "First Name": Column(
                name="first_name", 
                settable=True,
                insert_prompt="What's this pilot's first name?",
                update_prompt="What's this pilot's new first name?",
                is_valid=lambda x : 0 < len(x) <= 40,
                validation_prompt="A pilot's first name must be between 1 and 40 characters inclusive"
            ),
            "Last Name": Column(
                name="last_name", 
                settable=True,
                insert_prompt="What's this pilot's last name?",
                update_prompt="What's this pilot's new last name?",
                is_valid=lambda x : 0 < len(x) <= 40,
                validation_prompt="A pilot's last name must be between 1 and 40 characters inclusive"
            ),
            "Date of Birth": Column(
                name="date_of_birth", 
                settable=True,
                insert_prompt="What's this pilot's date of birth in YYYY-MM-DD format?",
                update_prompt="What's this pilot's new date of birth in YYYY-MM-DD format?",
                is_valid=validate_date, 
                validation_prompt="A pilot's date of birth must be in the format YYYY-MM-DD"
            ),
        }

    def create_table(self) -> None:
        try:
            self.db.cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS pilots (
                        pilot_id INTEGER PRIMARY KEY, 
                        first_name VARCHAR(40) NOT NULL,
                        last_name VARCHAR(40) NOT NULL,
                        date_of_birth VARCHAR(19) NOT NULL
                    );
                """
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to create pilots table")

    # values = (first_name, last_name, date_of_birth)
    def insert(self, values: tuple[str]) -> Pilot:
        try:
            self.db.cursor.execute(
                """
                    INSERT INTO pilots 
                    VALUES (NULL, ?, ?, ?)
                    RETURNING pilot_id;
                """,
                values
            )

            pilot = Pilot(self.db.cursor.fetchone()[0], *values) 

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to insert into pilots table")
        else:
            return pilot

    def update(self, pilot_id: int, column_name: str, new_value: str) -> Pilot:
        try:
            self.db.cursor.execute(
                f"""
                    UPDATE pilots 
                    SET {column_name} = ?
                    WHERE pilot_id = ?
                    RETURNING *;
                """,
                (new_value, pilot_id)
            )

            pilot = Pilot(*self.db.cursor.fetchone())  

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to update pilots table")
        else:
            return pilot

    def get_all(self) -> Iterable[Pilot]:
        try:
            self.db.cursor.execute("SELECT * FROM pilots;")
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get all rows in pilots table")
        else:
            return map(lambda row : Pilot(*row), rows) 

    def get(self, column_name: str, value: str) -> Iterable[Pilot]:
        try:
            self.db.cursor.execute(
                f"""
                    SELECT *
                    FROM pilots
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get rows based on a column in pilots table")
        else:
            return map(lambda row : Pilot(*row), rows) 

    def delete_and_return(self, column_name: str, value: str) -> Iterable[Pilot]:
        try:
            self.db.cursor.execute(
                f"""
                    DELETE FROM pilots
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to delete from pilots table")
        else:
            return self.get_all()

    def exists(self, pilot_id: int) -> bool:
        try:
            self.db.cursor.execute(
                """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM pilots 
                        WHERE pilot_id = ?
                    );
                """,
                (pilot_id,)
            )
            exists = self.db.cursor.fetchone()[0]
        except:
            self.db.handle_error("Unable to determine if pilot exists")
        else:
            return False if exists == 0 else True