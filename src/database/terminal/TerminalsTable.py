from typing import Iterable
from database.terminal.Terminal import Terminal, ExtendedTerminal
from database.Table import Table, Column
from cli.TextTable import TextTable

class TerminalsTable(Table):
    def __init__(self, database):
        super().__init__(database)
        
        self.columns = { 
            "Terminal ID": Column(
                name="terminals.terminal_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.exists(x),
                validation_prompt="A terminal's ID must be a non negative integer and must exist in the database"
            ),
            "Airport ID": Column(
                name="terminals.airport_id", 
                settable=True,
                insert_prompt="What's the ID of the airport where this terminal is located?",
                update_prompt="What's the ID of the new airport where this terminal is located?",
                is_valid=lambda x : x.isdigit() and self.db.airports.exists(x),
                validation_prompt="A terminal's airport ID must be a non negative integer and must exist in the database"
            ),
            "Name": Column(
                name="name", 
                settable=True,
                insert_prompt="What's the name of this terminal?",
                update_prompt="What's the new name of this terminal?",
                is_valid=lambda x : 0 < len(x) <= 100,
                validation_prompt="An terminal's name must be between 1 and 100 characters inclusive"
            )
        }

    def create_table(self) -> None:
        try:
            self.db.cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS terminals (
                        terminal_id INTEGER PRIMARY KEY,
                        airport_id INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL,

                        FOREIGN KEY (airport_id) REFERENCES airports ON DELETE CASCADE
                    );
                """
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to create terminals table")

    # values = (airport_id, name)
    def insert(self, values: tuple[str]) -> Terminal:
        try:
            self.db.cursor.execute(
                """
                    INSERT INTO terminals 
                    VALUES (NULL, ?, ?)
                    RETURNING terminal_id;
                """,
                values
            )

            terminal = Terminal(self.db.cursor.fetchone()[0], *values) 

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to insert into terminals table")
        else:
            return terminal

    def update(self, terminal_id: int, column_name: str, new_value: str) -> Terminal:
        try:
            self.db.cursor.execute(
                f"""
                    UPDATE terminals 
                    SET {column_name} = ?
                    WHERE terminal_id = ?
                    RETURNING *;
                """,
                (new_value, terminal_id)
            )

            terminal = Terminal(*self.db.cursor.fetchone())  

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to update terminals table")
        else:
            return terminal

    # returns an ExtendedTerminal which is a Terminal that also contains information about the airport
    def get_all(self) -> Iterable[ExtendedTerminal]: 
        try:
            self.db.cursor.execute(
                """
                    SELECT terminal_id, terminals.name, airports.airport_id, airports.name, airports.address
                    FROM terminals
                    JOIN airports ON terminals.airport_id = airports.airport_id;
                """
            )
            rows = self.db.cursor.fetchall()
        except: 
            self.db.handle_error("Unable to get all rows in terminals table")
        else:
            return map(lambda row : ExtendedTerminal(*row), rows) 

    def get(self, column_name: str, value: str) -> Iterable[ExtendedTerminal]:
        try:
            self.db.cursor.execute(
                f"""
                    SELECT terminal_id, terminals.name, airports.airport_id, airports.name, airports.address
                    FROM terminals
                    JOIN airports ON terminals.airport_id = airports.airport_id
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get rows based on a column in terminals table")
        else:
            return map(lambda row : ExtendedTerminal(*row), rows) 

    def delete_and_return(self, column_name: str, value: str) -> Iterable[ExtendedTerminal]:
        try:
            self.db.cursor.execute(
                f"""
                    DELETE FROM terminals
                    WHERE {column_name} = ?;
                """,
                (value,)
            )

            self.db.connection.commit()

            self.db.cursor.execute("SELECT * FROM terminals;")
            remaining_rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to delete from terminals table")
        else:
            return map(lambda row : Terminal(*row), remaining_rows) 

    def exists(self, terminal_id: int) -> bool:
        try:
            self.db.cursor.execute(
                """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM terminals 
                        WHERE terminal_id = ?
                    );
                """,
                (terminal_id,)
            )
            exists = self.db.cursor.fetchone()[0]
        except:
            self.db.handle_error("Unable to determine if terminal exists")
        else:
            return False if exists == 0 else True