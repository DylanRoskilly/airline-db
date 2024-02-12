from cli.menus.Menu import Menu
from cli.TextTable import TextTable 

class InsertMenu(Menu):
    def print_menu(self) -> None:
        print("""
+---------------------------------------------+
|                INSERT MENU                  |
+---------------------------------------------+
|   1. Insert a new pilot                     |
|   2. Insert a new customer                  |
|   3. Insert a new aircraft                  |
|   4. Insert a new airport                   |
|   5. Insert a new terminal                  |
|   6. Insert a new flight                    |
|   7. Assign a pilot to a flight             |
|   8. Assign a customer to a flight          |
|   0. Go back to the main menu               |
+---------------------------------------------+
        """)
    
    def respond(self, option: str) -> None:
        # if option meets these conditions then we can use the table classes
        if option.isdigit() and 1 <= int(option) <= 6:
            # get the Table for the inputted option
            table = getattr(self.db, self.options[int(option) - 1])

            values = []
            # loop through each column and get a valid value for each column in the table
            for column in table.columns:
                if table.columns[column].settable:
                    value = self.get_valid_input(
                        prompt=table.columns[column].insert_prompt,
                        is_valid=table.columns[column].is_valid,
                        error_message=table.columns[column].validation_prompt
                    )
                    if value is None:
                        return
                    values.append(value)

            result = table.insert(tuple(values)) 

            text_table = TextTable(result.get_column_names())
            text_table.add_row(result.to_row())

            print("Successfully inserted:") 
            print(text_table.get_string())
        elif option == "7": # assign a pilot to a flight
            pilot_id = self.get_valid_input(
                prompt="What's the ID of the pilot that you want to assign a flight to?",
                is_valid=lambda x : x.isdigit() and self.db.pilots.exists(x),
                error_message="Pilot ID's must be a non negative integer and exist in the database."
            )
            if pilot_id is None:
                return

            flight_id = self.get_valid_input(
                prompt="What's the ID of the flight that you want to assign this pilot to?",
                is_valid=lambda x : x.isdigit() and self.db.flights.exists(x),
                error_message="Flight ID's must be a non negative integer and exist in the database."
            ) 
            if flight_id is None:
                return

            # cannot add a pilot to a flight that theyre already on
            if self.db.flight_pilots.exists(flight_id, pilot_id):
                print("That pilot is already on that flight. Press Enter to go back to the menu.") 
                self.get_input()
                return

            flight_pilot = self.db.flight_pilots.insert(flight_id, pilot_id)
            print(f"Pilot with ID: {flight_pilot.pilot_id} has been added to the flight with ID: {flight_pilot.flight_id}") 
        elif option == "8": # assign a customer to a flight
            customer_id = self.get_valid_input(
                prompt="What's the ID of the customer that you want to assign a seat?",
                is_valid=lambda x : x.isdigit() and self.db.customers.exists(x),
                error_message="Customer ID's must be a non negative integer and exist in the database."
            ) 
            if customer_id is None:
                return

            flight_id = self.get_valid_input(
                prompt="What's the ID of the flight that you want to assign this customer's seat to?",
                is_valid=lambda x : x.isdigit() and self.db.flights.exists(x),
                error_message="Flight ID's must be a non negative integer and exist in the database."
            ) 
            if flight_id is None:
                return

            # cannot add a customer to a flight that theyre already on
            if self.db.flight_passengers.exists(flight_id, customer_id):
                print("That customer is already on that flight. Press Enter to go to back to the menu.")
                self.get_input()
                return
            
            option = self.get_valid_input(
                prompt="How do you want to assign this customer a seat?\n   1. Manually\n   2. Use next available seat",
                is_valid=lambda x : x == "1" or x == "2",
                error_message="Must enter 1 or 2."
            )
            if option is None:
                return

            seat_number = None
            if option == "1":
                max_passengers = self.db.flight_passengers.get_max_passengers(flight_id)
                seat_number = self.get_valid_input(
                    prompt="What's the seat number for this customer?",
                    is_valid=lambda x : x.isdigit() and 1 <= int(x) <= max_passengers, 
                    error_message=f"Seat number must be an integer between 1 and {max_passengers} (the maximum passengers for this flight) (inclusive)"
                )  
                if seat_number is None:
                    return
                
                if not self.db.flight_passengers.is_seat_available(flight_id, seat_number):
                    print("That seat is taken by another customer on this flight. Press Enter to go back to the menu.")
                    self.get_input()
                    return
            elif option == "2":
                seat_number = self.db.flight_passengers.get_next_available_seat(flight_id)
                # seat_number is None if there are no more seats available
                if seat_number is None:
                    print("There are no more available seats on this flight. Press Enter to go back to the menu.")
                    self.get_input()
                    return
                    
            flight_passenger = self.db.flight_passengers.insert(flight_id, customer_id, seat_number)
            print(f"Customer with ID: {flight_passenger.customer_id} has been added to the flight with ID: {flight_passenger.flight_id} with seat number: {flight_passenger.seat_number}") 

        print("Press Enter to go to back to the insert menu.")
        self.get_input()