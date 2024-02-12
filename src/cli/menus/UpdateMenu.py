from cli.menus.Menu import Menu
from cli.TextTable import TextTable

class UpdateMenu(Menu):
    def print_menu(self) -> None:
        print("""
+---------------------------------------------+
|                UPDATE MENU                  |
+---------------------------------------------+
|   1. Update a pilot                         |
|   2. Update a customer                      |
|   3. Update an aircraft                     |
|   4. Update an airport                      |
|   5. Update a terminal                      |
|   6. Update a flight                        |
|   7. Update a passenger's seat number       |
|   0. Go back to the main menu               |
+---------------------------------------------+
        """)
    
    def respond(self, option: str) -> None:
        if option.isdigit() and 1 <= int(option) <= 6: # standard options
            option = int(option)
            table = getattr(self.db, self.options[option - 1]) # get table for option
            table_name = self.options[option - 1][:-1] # get table name as singular

            id = self.get_valid_input(
                prompt=f"What's the ID of the {table_name} you want to update?",
                is_valid=lambda x : x.isdigit(),
                error_message="ID must be a positive integer."
            )  
            if id is None:
                return
            
            # make sure that the inputted id exists in the table
            if not table.exists(id):
                print(f"No {table_name} with that ID exists. Press Enter to go to back to the menu.")
                self.get_input()
                return

            (column_names, options) = table.get_column_choices(False)
            option = self.get_valid_input(
                prompt="What column do you want to update?" + options,
                is_valid=lambda x : x.isdigit() and 0 < int(x) <= len(column_names),
                error_message=f"Must be an integer between 1 and {len(column_names)} inclusive."
            )  
            if option is None:
                return

            column = table.columns[column_names[int(option)-1]] # get the Column for the inputted column

            new_value = self.get_valid_input(
                prompt=column.update_prompt,
                is_valid=column.is_valid,
                error_message=column.validation_prompt
            )  
            if new_value is None:
                return

            result = table.update(id, column.name, new_value)

            text_table = TextTable(result.get_column_names())
            text_table.add_row(result.to_row())

            print("Successfully updated. Here's the updated row:") 
            print(text_table.get_string()) 
        elif option == "7": # update seat number
            customer_id = self.get_valid_input(
                prompt="What's the ID of the customer whose seat number you want to update?",
                is_valid=lambda x : x.isdigit() and self.db.customers.exists(x),
                error_message=f"Customer ID must be a non negative integer and exist in the database."
            )  
            if customer_id is None:
                return

            flight_id = self.get_valid_input(
                prompt="What's the ID of the flight?",
                is_valid=lambda x : x.isdigit() and self.db.flights.exists(x),
                error_message=f"Flight ID must be a non negative integer and exist in the database."
            )  
            if flight_id is None:
                return

            # customer must be on the flight to be able to update their seat
            if not self.db.flight_passengers.exists(flight_id, customer_id):
                print("That customer is not on that flight. Press Enter to go to back to the menu.")
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
                    prompt="What's the new seat number for this customer?",
                    is_valid=lambda x : x.isdigit() and 1 <= int(x) <= max_passengers, 
                    error_message=f"Seat number must be an integer between 1 and {max_passengers} (the maximum passengers for this flight) (inclusive)"
                )  
                if seat_number is None:
                    return
                
                # determine if inputted seat is available
                if not self.db.flight_passengers.is_seat_available(flight_id, seat_number):
                    print("That seat is taken by another customer on this flight. Press Enter to go back to the menu.")
                    self.get_input()
                    return
            elif option == "2":
                seat_number = self.db.flight_passengers.get_next_available_seat(flight_id)
                # seat_number is None if there are no more available seats
                if seat_number is None:
                    print("There are no more available seats on this flight. Press Enter to go back to the menu.")
                    self.get_input()
                    return

            flight_passenger = self.db.flight_passengers.update_seat_number(flight_id, customer_id, seat_number) 
            print(f"The seat number of customer with ID: {flight_passenger.customer_id} on flight with ID: {flight_passenger.flight_id} has been changed to {flight_passenger.seat_number}") 

        print("Press Enter to go to back to the update menu.")
        self.get_input()