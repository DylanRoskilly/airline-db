from cli.menus.Menu import Menu
from cli.Paginator import Paginator
from cli.TextTable import TextTable

class StatisticsMenu(Menu):
    def __init__(self, database):
        super().__init__(database)
        self.days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    def print_menu(self) -> None:
        print("""
+-----------------------------------------------------------+
|                     STATISTICS MENU                       |
+-----------------------------------------------------------+
|   1. Get number of flights per week                       |
|   2. Get number of flights to a destination per month     |
|   3. Rank days of the week based on the most customers    |
|   4. Get a pilot's total time in the air                  |
|   5. Rank a pilot's days of the week based on flights     |
|   6. Rank destinations by popularity                      |
|   7. Rank upcoming flights by percentage of used up seats |
|   8. Rank pilots by total number of flights               |
|   9. Rank customers by their number of flights            |
|  10. Get number of passengers on a flight                 |
|  11. Get number of pilots on a flight                     |
|   0. Go back to the main menu                             |
+-----------------------------------------------------------+
        """) 

    def respond(self, option: str) -> None:
        text_table = None # initialise a variable that stores the text table for the calculated stats

        match option:
            case "1": 
                try:
                    self.db.cursor.execute(
                        """
                            SELECT strftime('%Y', arrival_time) as year, strftime('%W', arrival_time) as week, COUNT(flight_id) as num_of_flights
                            FROM flights
                            GROUP BY week, year
                            ORDER BY arrival_time DESC;
                        """
                    )
                    rows = self.db.cursor.fetchall()
                except:
                    self.db.handle_error("Unable to get number of flights per week from database")
                else:
                    if len(rows) == 0 or rows is None or rows[0] is None:
                        print("No flights in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Year", "Week Number", "Number of Flights"])
                    for (year, week, num_of_flights) in rows:
                        text_table.add_row([year, week, str(num_of_flights)])

                    print("Here's the number of flights per week:") 
            case "2":
                destination = self.get_valid_input(
                    prompt="What destination do you want to find the flights per month for?",
                    is_valid=lambda x: 0 < len(x) <= 100,
                    error_message="Destination must be between 1 and 100 characters inclusive."
                )
                if destination is None:
                    return

                try:
                    self.db.cursor.execute(
                        """
                            SELECT strftime('%Y', arrival_time) as year, strftime('%m', arrival_time) as month, COUNT(flight_id) as num_of_flights
                            FROM flights
                            WHERE destination = ? 
                            GROUP BY month, year
                            ORDER BY arrival_time DESC;
                        """,
                        (destination,)
                    ) 
                    rows = self.db.cursor.fetchall()
                except:
                    self.db.handle_error("Unable to get number of flights to a destination per month from database")
                else:
                    if len(rows) == 0 or rows is None or rows[0] is None:
                        print("No flights for that destination in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Year", "Month", "Number of Flights"])
                    for (year, month, num_of_flights) in rows:
                        text_table.add_row([year, month, str(num_of_flights)])

                    print("Here's the number of flights per month for this destination:")
            case "3":
                try:
                    self.db.cursor.execute(
                        """
                            SELECT strftime('%w', boarding_time) as day_of_week, COUNT(customer_id) as num_of_customers
                            FROM flights
                            LEFT JOIN flight_passengers ON flights.flight_id = flight_passengers.flight_id
                            GROUP BY day_of_week
                            ORDER BY num_of_customers DESC;
                        """
                    )
                    rows = self.db.cursor.fetchall()
                except:
                    self.db.handle_error("Unable to get data to rank days of the week. Press Enter to go back to the stats menu.")
                else:
                    if len(rows) == 0 or rows is None or rows[0] is None:
                        print("No flights in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Day of Week", "Number of Customers"])
                    for (day_of_week, num_of_customers) in rows:
                        # use self.days to convert a positive integer representing day of week to 
                        # a string for the name of the day of the week
                        text_table.add_row([self.days[int(day_of_week) - 1], str(num_of_customers)])

                    print("Here's the ranking of days of the week based on the most amount of customer:")
            case "4": 
                pilot_id = self.get_valid_input(
                    prompt="What's the ID of the pilot that you want to find their total time in the air?",
                    is_valid=lambda x: x.isdigit() and self.db.pilots.exists(x),
                    error_message="Pilot ID must be a non negative integer and must exist in the database."
                )
                if pilot_id is None:
                    return

                try:
                    self.db.cursor.execute(
                        """
                            SELECT SUM(unixepoch(arrival_time) - unixepoch(departure_time)) as seconds
                            FROM flights
                            JOIN flight_pilots ON flights.flight_id = flight_pilots.flight_id
                            WHERE pilot_id = ? AND arrival_time <= date('now');
                        """,
                        (pilot_id,)
                    )
                    seconds = self.db.cursor.fetchone()
                except:
                    self.db.handle_error("Unable to get pilot's total air time from database")
                else:
                    if seconds is None or seconds[0] is None:
                        print("This pilot has been on no flights in the past. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Time in the Air (hours)"])
                    # convert seconds to hours and round to 2 dp
                    text_table.add_row([str(round(seconds[0] / 3600, 2))])

                    print("Here's the total time this pilot has spent in the air:")
            case "5":
                pilot_id = self.get_valid_input(
                    prompt="What's the ID of the pilot that you want to find their busiest days of the week for?",
                    is_valid=lambda x : x.isdigit() and self.db.pilots.exists(x),
                    error_message="Pilot ID must be a non negative integer and must exist in the database."
                )
                if pilot_id is None:
                    return

                try:
                    self.db.cursor.execute(
                        """
                            SELECT strftime('%w', boarding_time) as day_of_week, COUNT(flight_pilots.flight_id) as num_of_flights
                            FROM flights
                            JOIN flight_pilots ON flights.flight_id = flight_pilots.flight_id
                            WHERE pilot_id = ?
                            GROUP BY day_of_week
                            ORDER BY num_of_flights DESC;
                        """,
                        (pilot_id,)
                    )
                    rows = self.db.cursor.fetchall()
                except:
                    self.db.handle_error("Unable to get pilot's days of the week from the database")
                else:
                    if len(rows) == 0 or rows is None or rows[0] is None:
                        print("This pilot has no flights in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Day of Week", "Number of Flights"])
                    for (day_of_week, num_of_flights) in rows:
                        text_table.add_row([self.days[int(day_of_week) - 1], str(num_of_flights)])

                    print("Here's the ranking of this pilot's days of the week based on their number of flights:")
            case "6":
                try:
                    self.db.cursor.execute(
                        """
                            SELECT destination, COUNT(customer_id) AS num_of_passengers
                            FROM flights
                            LEFT JOIN flight_passengers ON flights.flight_id = flight_passengers.flight_id
                            GROUP BY destination
                            ORDER BY num_of_passengers DESC;
                        """
                    )
                    rows = self.db.cursor.fetchall()
                except:
                    self.db.handle_error("Unable to get destination popularity from database")
                else:
                    if len(rows) == 0 or rows is None or rows[0] is None:
                        print("There are no flights in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Destination", "Number of Passengers"])
                    for (destination, num_of_passengers) in rows:
                        text_table.add_row([destination, str(num_of_passengers)])

                    print("Here's the rankings of destinations by popularity:")
            case "7":
                try:
                    self.db.cursor.execute(
                        """
                            SELECT flights.flight_id, flights.aircraft_id, airports.name, terminals.name, flights.boarding_time, destination, COUNT(customer_id) AS num_of_passengers, aircrafts.max_passengers
                            FROM flights
                            LEFT JOIN flight_passengers ON flights.flight_id = flight_passengers.flight_id
                            JOIN aircrafts ON flights.aircraft_id = aircrafts.aircraft_id
                            JOIN terminals ON flights.terminal_id = terminals.terminal_id
                            JOIN airports ON terminals.airport_id = airports.airport_id
                            WHERE boarding_time >= date('now')
                            GROUP BY flights.flight_id;
                        """
                    )
                    rows = self.db.cursor.fetchall()
                except:
                    self.db.handle_error("Unable to get percentage of used up seats from database")
                else:
                    if len(rows) == 0 or rows is None or rows[0] is None:
                        print("There are no flights in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return
                      
                    rows.sort(key=lambda row: row[6] / row[7], reverse=True)
                  
                    text_table = TextTable(["Flight ID", "Aircraft ID", "Airport Name", "Terminal Name", "Boarding Time", "Destination", "Percentage"])
                    for (flight_id, aircraft_id, airport, terminal, boarding_time, destination, num_of_passengers, max_passengers) in rows:
                        # calculate percentage and round to 2 dp
                        text_table.add_row([str(flight_id), str(aircraft_id), airport, terminal, boarding_time, destination, str(round((num_of_passengers / max_passengers) * 100, 2))])

                    print("Here's the ranking of upcoming flights by percentage of used up seats:")
            case "8":
                try:
                    self.db.cursor.execute(
                        """
                            SELECT pilots.pilot_id, first_name, last_name, COUNT(flight_pilots.pilot_id) AS num_of_flights
                            FROM flight_pilots
                            RIGHT JOIN pilots ON flight_pilots.pilot_id = pilots.pilot_id
                            GROUP BY pilots.pilot_id
                            ORDER BY num_of_flights DESC;
                        """
                    )
                    rows = self.db.cursor.fetchall()
                except:
                    self.db.handle_error("Unable to rank pilots based on their number of flights")
                else:
                    if len(rows) == 0 or rows is None or rows[0] is None:
                        print("There are no pilots who have been on a flight in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Pilot ID", "First Name", "Last Name", "Number of Flights"])
                    for (pilot_id, first_name, last_name, num_of_flights) in rows:
                        text_table.add_row([str(pilot_id), first_name, last_name, str(num_of_flights)])

                    print("Here's the rankings of pilots by their total number of flights:")
            case "9":
                try:
                    self.db.cursor.execute(
                        """
                            SELECT customers.customer_id, first_name, last_name, COUNT(flight_passengers.customer_id) AS num_of_flights
                            FROM flight_passengers
                            RIGHT JOIN customers ON flight_passengers.customer_id = customers.customer_id
                            GROUP BY customers.customer_id
                            ORDER BY num_of_flights DESC;
                        """
                    )
                    rows = self.db.cursor.fetchall()
                except:
                    self.db.handle_error("Unable to rank customers based on their number of flights")
                else:
                    if len(rows) == 0 or rows is None or rows[0] is None:
                        print("There are no customers who have been on a flight in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Customer ID", "First Name", "Last Name", "Number of Flights"])
                    for (pilot_id, first_name, last_name, num_of_flights) in rows:
                        text_table.add_row([str(pilot_id), first_name, last_name, str(num_of_flights)])

                    print("Here's the rankings of customers by their number of flights:")
            case "10":
                flight_id = self.get_valid_input(
                    prompt="What's the ID of the flight that you want to find the number of passengers on?",
                    is_valid=lambda x: x.isdigit() and self.db.flights.exists(x),
                    error_message="Flight ID must be a non negative integer and must exist in the database."
                )
                if flight_id is None:
                    return

                try:
                    self.db.cursor.execute(
                        """
                            SELECT flights.flight_id, flights.destination, max_passengers, COUNT(flight_passengers.customer_id) AS num_of_passengers
                            FROM flights
                            LEFT JOIN flight_passengers ON flights.flight_id = flight_passengers.flight_id
                            JOIN aircrafts ON flights.aircraft_id = aircrafts.aircraft_id
                            WHERE flights.flight_id = ?;
                        """,
                        (flight_id,)
                    )
                    (flight_id, destination, max_passengers, num_of_passengers) = self.db.cursor.fetchone()
                except:
                    self.db.handle_error("Unable to get number of passengers on flight")
                else:
                    # determine if any flights even exist
                    if flight_id is None or destination is None:
                        print("That flight does not exist in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Flight ID", "Destination", "Max Passengers", "Current No. Passengers", "Percentage"])
                    text_table.add_row([str(flight_id), destination, str(max_passengers), str(num_of_passengers), str(round((num_of_passengers / max_passengers) * 100, 2))])

                    print("Here's the numbers of passengers on this flight:")
            case "11":
                flight_id = self.get_valid_input(
                    prompt="What's the ID of the flight that you want to find the number of pilots on?",
                    is_valid=lambda x: x.isdigit() and self.db.flights.exists(x),
                    error_message="Flight ID must be a non negative integer and must exist in the database."
                )
                if flight_id is None:
                    return

                try:
                    self.db.cursor.execute(
                        """
                            SELECT flights.flight_id, flights.destination, COUNT(flight_pilots.pilot_id) AS num_of_pilots
                            FROM flights
                            LEFT JOIN flight_pilots ON flights.flight_id = flight_pilots.flight_id
                            WHERE flights.flight_id = ?;
                        """,
                        (flight_id,)
                    )
                    (flight_id, destination, num_of_pilots) = self.db.cursor.fetchone()
                except:
                    self.db.handle_error("Unable to get number of pilots on flight")
                else:
                    if flight_id is None or destination is None:
                        print("That flight does not exist in the database. Press Enter to go back to the stats menu.")
                        self.get_input()
                        return

                    text_table = TextTable(["Flight ID", "Destination", "Number of Pilots"])
                    text_table.add_row([str(flight_id), destination, str(num_of_pilots)])

                    print("Here's the number of pilots on this flight:")

        paginator = Paginator(text_table)
        paginator.start()