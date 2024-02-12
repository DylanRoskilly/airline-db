import sqlite3
import sys
from database.pilot.PilotsTable import PilotsTable
from database.airport.AirportsTable import AirportsTable
from database.terminal.TerminalsTable import TerminalsTable
from database.customer.CustomersTable import CustomersTable
from database.aircraft.AircraftsTable import AircraftsTable
from database.flight.FlightsTable import FlightsTable
from database.flight_passenger.FlightPassengersTable import FlightPassengersTable
from database.flight_pilot.FlightPilotsTable import FlightPilotsTable

class Database:
    def __init__(self, db_name: str = "airline"):
        self.db_name = db_name # the name of the database file
        
        # each table has their own property in this class so they can be easily accessed from the menus
        self.pilots = PilotsTable(self)
        
        self.airports = AirportsTable(self)
        self.terminals = TerminalsTable(self)

        self.customers = CustomersTable(self)

        self.aircrafts = AircraftsTable(self)

        self.flights = FlightsTable(self)
        self.flight_passengers = FlightPassengersTable(self)
        self.flight_pilots = FlightPilotsTable(self)

    def connect(self) -> None:
        try:
            self.connection = sqlite3.connect(f"{self.db_name}.db")
        except:
            self.handle_error("Unable to connect to the database")

        try:
            self.connection.execute("PRAGMA foreign_keys = ON;") # foreign keys have to be enabled manually in sqlite
        except:
            self.handle_error("Unable to enable foreign keys")

        try:
            self.cursor = self.connection.cursor()
        except:
            self.handle_error("Unable to make a cursor")

    # creates the tables if they do not exist
    def create_tables(self) -> None:
        self.pilots.create_table()
        
        self.airports.create_table()
        self.terminals.create_table()

        self.customers.create_table()

        self.aircrafts.create_table()

        self.flights.create_table()
        self.flight_passengers.create_table()
        self.flight_pilots.create_table()

    # responds to a database error. for now, terminates the program if theres an error
    def handle_error(self, error_message) -> None:
        print(error_message + "... Exiting...")
        sys.exit(0)
    
    # we must close cursor and connection before dropping this class from memory
    # otherwise there will be opened connections not being used
    def __exit__(self):
        self.cursor.close()
        self.connection.close()