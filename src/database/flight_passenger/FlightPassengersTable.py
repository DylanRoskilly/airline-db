from typing import Iterator
from database.flight_passenger.FlightPassenger import FlightPassenger 
from database.customer.Customer import Customer 
from database.Table import Table, Column
from cli.TextTable import TextTable

class FlightPassengersTable(Table):
    def __init__(self, database):
        super().__init__(database)
        
        self.columns = { 
            "Flight ID": Column(
                name="flight_passengers.flight_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.db.flights.exists(x),
                validation_prompt="A flight's ID must be a non negative integer and must exist in the database"
            ),
            "Customer ID": Column(
                name="flight_passengers.customer_id", 
                settable=False,
                is_valid=lambda x : x.isdigit() and self.db.customers.exists(x),
                validation_prompt="A customer's ID must be a non negative integer and must exist in the database"
            ),
            "Seat Number": Column(
                name="seat_number", 
                settable=True,
                insert_prompt="What's this customer's seat number?",
                update_prompt="What's this customer's new seat number?",
                is_valid=lambda x : x.isdigit(),
                validation_prompt="A customer's seat number must be a non negative integer"
            ),
        }

    def create_table(self) -> None:
        try:
            self.db.cursor.execute(
              """
                  CREATE TABLE IF NOT EXISTS flight_passengers (
                      flight_id INTEGER,
                      customer_id INTEGER,
                      seat_number INTEGER NOT NULL,
    
                      PRIMARY KEY (flight_id, customer_id),
                      FOREIGN KEY (flight_id) REFERENCES flights ON DELETE CASCADE,
                      FOREIGN KEY (customer_id) REFERENCES customers ON DELETE CASCADE
                  );
              """
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to create flight passengers table")

    # adds the customer to the flight and assigns them to seat_number
    def insert(self, flight_id: int, customer_id: int, seat_number: int) -> FlightPassenger:
        try:
            self.db.cursor.execute(
                """
                    INSERT INTO flight_passengers 
                    VALUES (?, ?, ?);
                """,
                (flight_id, customer_id, seat_number)
            )
            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to insert into flight passengers table")
        else:
            return FlightPassenger(flight_id, customer_id, seat_number)  

    # modify a customer's seat number on a flight
    def update_seat_number(self, flight_id: int, customer_id: int, seat_number: int) -> FlightPassenger:
        try:
            self.db.cursor.execute(
                """
                    UPDATE flight_passengers 
                    SET seat_number = ?
                    WHERE flight_id = ? AND customer_id = ?
                    RETURNING *;
                """,
                (seat_number, flight_id, customer_id)
            )

            flight_passenger = FlightPassenger(*self.db.cursor.fetchone()) 

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to update seat number in flight passengers table")
        else:
            return flight_passenger

    # returns all customers on a flight
    def get(self, flight_id: str) -> Iterator[Customer]:
        try:
            self.db.cursor.execute(
                """
                    SELECT customers.customer_id, first_name, last_name, date_of_birth, home_address, phone_number
                    FROM flight_passengers
                    JOIN customers ON customers.customer_id = flight_passengers.customer_id
                    WHERE flight_id = ?;
                """, 
                (flight_id,)
            )
            rows = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get customers from flight passengers table")
        else:
            return map(lambda row : Customer(*row), rows) 

    # removes a customer from a flight and returns the remaining customers on the flight
    def delete_and_return(self, flight_id: int, customer_id: int) -> Iterator[Customer]:
        try:
            self.db.cursor.execute(
                """
                    DELETE FROM flight_passengers
                    WHERE flight_id = ? AND customer_id = ?;
                """,
                (flight_id, customer_id)
            )

            self.db.connection.commit()
        except:
            self.db.handle_error("Unable to delete from flight passengers table")
        else:
            return self.get(flight_id) 

    # determines if a customer is on a flight
    def exists(self, flight_id: int, customer_id: int) -> bool:
        try:
            self.db.cursor.execute(
                """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM flight_passengers 
                        WHERE flight_id = ? AND customer_id = ?
                    );
                """,
                (flight_id, customer_id)
            )
            exists = self.db.cursor.fetchone()[0]
        except:
            self.db.handle_error("Unable to determine if flight passenger exist")
        else:
            return False if exists == 0 else True
    
    # finds the maximum number of passengers on a flight (based on the aircraft)
    def get_max_passengers(self, flight_id: int) -> int:
        try:
            self.db.cursor.execute(
                """
                    SELECT max_passengers
                    FROM flights
                    JOIN aircrafts ON flights.aircraft_id = flights.aircraft_id
                    WHERE flight_id = ?;
                """,
                (flight_id,)
            )
            max_passengers = self.db.cursor.fetchone()[0]
        except:
            self.db.handle_error("Unable to get max passengers")
        else:
            return max_passengers

    # determines if seat_number is available on the flight with id flight_id
    def is_seat_available(self, flight_id: int, seat_number: int) -> bool:
        try:
            self.db.cursor.execute(
                """
                    SELECT EXISTS(
                        SELECT 1 
                        FROM flight_passengers 
                        WHERE flight_id = ? AND seat_number = ?
                    );
                """,
                (flight_id, seat_number)
            )
            exists = self.db.cursor.fetchone()[0]
        except:
            self.db.handle_error("Unable to determine if seat is available")
        else:
            return True if exists == 0 else False

    # returns the next available seat on flight with id flight_id
    # returns None if there are no more available seats
    def get_next_available_seat(self, flight_id: int) -> int | None: 
        try:
            self.db.cursor.execute(
                """
                    SELECT seat_number
                    FROM flight_passengers
                    WHERE flight_id = ?
                    ORDER BY seat_number;
                """,
                (flight_id,)
            )
            seat_numbers = self.db.cursor.fetchall()
        except:
            self.db.handle_error("Unable to get taken seats from database")
        else: 
            last = 0 
            for (seat_number) in seat_numbers:
                if last+1 != seat_number:
                    return last+1
                last = seat_number

            return last+1 if last+1 <= self.get_max_passengers(flight_id) else None