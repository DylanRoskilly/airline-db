from typing import Iterator
from database.customer.Customer import Customer 
from database.Table import Table, Column
from database.validation import validate_date
from cli.TextTable import TextTable

class CustomersTable(Table):
    def __init__(self, database):
        super().__init__(database)
        
        self.columns = {
            "Customer ID": Column(
                name="customers.customer_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.exists(x),
                validation_prompt="A customer's ID must be a non negative integer and must exist in the database"
            ),
            "First Name": Column(
                name="first_name", 
                settable=True, 
                insert_prompt="What's the first name of this customer?", 
                update_prompt="What's this customer's new first name?", 
                is_valid=lambda x : 0 < len(x) <= 40,
                validation_prompt="A customer's first name must be between 0 and 40 characters"
            ),
            "Last Name": Column(
                name="last_name", 
                settable=True,
                insert_prompt="What's the last name of this customer?",
                update_prompt="What's this customer's new last name?",
                is_valid=lambda x : 0 < len(x) <= 40,
                validation_prompt="A customer's last name must be between 0 and 40 characters"
            ),
            "Date of Birth": Column(
                name="date_of_birth", 
                settable=True,
                insert_prompt="What's this customer's date of birth in YYYY-MM-DD format?",
                update_prompt="What's this customer's new date of birth in YYYY-MM-DD format?",
                is_valid=validate_date,
                validation_prompt="A customer's date of birth must be in the YYYY-MM-DD format"
            ),
            "Home Address": Column(
                name="home_address", 
                settable=True,
                insert_prompt="What's this customer's home address?",
                update_prompt="What's this customer's new home address?",
                is_valid=lambda x : len(x) > 1, 
                validation_prompt="An customer's address must be more than 1 character"
            ),
            "Phone Number": Column(
                name="phone_number", 
                settable=True,
                insert_prompt="What's this customer's phone number?",
                update_prompt="What's this customer's new phone number?",
                is_valid=lambda x : 1 <= len(x) <= 15, 
                validation_prompt="An customer's phone number must be between 1 and 15 characters inclusive"
            )
        }

    def create_table(self) -> None:
        try:
            self.db.cursor.execute(
                """
                    CREATE TABLE IF NOT EXISTS customers (
                        customer_id INTEGER PRIMARY KEY,
                        first_name VARCHAR(40) NOT NULL,
                        last_name VARCHAR(40) NOT NULL,
                        date_of_birth VARCHAR(10) NOT NULL,
                        home_address TEXT NOT NULL,
                        phone_number VARCHAR(15)
                    );
                """
            )
            
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to create customers table")

    # values = (first_name, last_name, date_of_birth, home_address, phone_number)
    def insert(self, values: tuple[str]) -> Customer:
        try:
            self.db.cursor.execute(
                """
                    INSERT INTO customers 
                    VALUES (NULL, ?, ?, ?, ?, ?)
                    RETURNING customer_id;
                """,
                values
            )

            customer = Customer(self.db.cursor.fetchone()[0], *values)  

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to insert into customers table")
        else:
            return customer

    def update(self, customer_id: int, column_name: str, new_value: str) -> Customer:
        try:
            self.db.cursor.execute(
                f"""
                    UPDATE customers 
                    SET {column_name} = ?
                    WHERE customer_id = ?
                    RETURNING *;
                """,
                (new_value, customer_id)
            )

            customer = Customer(*self.db.cursor.fetchone())  

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to update customers table")
        else:
            return customer

    def get_all(self) -> Iterator[Customer]:
        try:
            self.db.cursor.execute("SELECT * FROM customers;")
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get all rows from customers table")
        else:
            return map(lambda row : Customer(*row), rows) 

    def get(self, column_name: str, value: str) -> Iterator[Customer]:
        try:
            self.db.cursor.execute(
                f"""
                    SELECT *
                    FROM customers
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get rows based on a column in customers table")
        else:
            return map(lambda row : Customer(*row), rows) 

    def delete_and_return(self, column_name: str, value: str) -> Iterator[Customer]:
        try:
            self.db.cursor.execute(
                f"""
                    DELETE FROM customers
                    WHERE {column_name} = ?;
                """,
                (value,)
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to delete from customers table")
        else:
            return self.get_all()

    def exists(self, customer_id: int) -> bool:
        try:
            self.db.cursor.execute(
                """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM customers 
                        WHERE customer_id = ?
                    );
                """,
                (customer_id,)
            )
            exists = self.db.cursor.fetchone()[0]
        except:
            self.db.handle_error("Unable to determine if customer exists")
        else:
            return False if exists == 0 else True