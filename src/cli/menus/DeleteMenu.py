from cli.menus.Menu import Menu
from cli.Paginator import Paginator
from cli.TextTable import TextTable

class DeleteMenu(Menu):
    def print_menu(self) -> None:
        print("""
+---------------------------------------------+
|                DELETE MENU                  |
+---------------------------------------------+
|   1. Delete a pilot                         |
|   2. Delete a customer                      |
|   3. Delete an aircraft                     |
|   4. Delete an airport                      |
|   5. Delete a terminal                      |
|   6. Delete a flight                        |
|   7. Remove a pilot from a flight           |
|   8. Remove a customer from a flight        |
|   0. Go back to the main menu               |
+---------------------------------------------+
        """)
    
    def respond(self, option: str) -> None:
        # initialise variable to store the remaining rows after the deletion
        # this will be used later
        remaining_rows = None 
        
        # if the inputted option meets these conditions then its a standard input
        # i.e. the table classes and their functions can be used
        if option.isdigit() and 1 <= int(option) <= 6: 
            table = getattr(self.db, self.options[int(option) - 1]) # get the table class for the option
            
            (column_names, options) = table.get_column_choices() # get the column options for the table
            # get the user to input an integer representing a column
            option = self.get_valid_input(
                prompt="What column do you want to delete by?" + options,
                is_valid=lambda x : x.isdigit() and 0 < int(x) <= len(column_names),
                error_message=f"Must be between 1 and {len(column_names)} inclusive."
            )
            if option is None:
                return
            
            column = table.columns[column_names[int(option)-1]] # get the Column class representing the column they chose

            value = self.get_valid_input(
                prompt="What values in this column do you want to delete rows by?",
                is_valid=column.is_valid,
                error_message=column.validation_prompt
            )
            if value is None:
                return
            
            remaining_rows = table.delete_and_return(column.name, value) # delete the rows from the table

            try:
                self.db.cursor.execute("SELECT changes();") # determine if any rows were deleted
                num_of_deleted_rows = self.db.cursor.fetchone()        
                if num_of_deleted_rows is None or num_of_deleted_rows[0] is None or num_of_deleted_rows[0] == 0:
                    print("No rows matched the critera. No rows deleted. Here are the rows of this table:") 
                else:
                    print(f"Successfully deleted {num_of_deleted_rows[0]} rows. Here are the remaining rows of this table:") 
            except:
                self.db.handle_error("Unable to get number of deleted rows")
        elif option == "7": # remove a pilot from a flight
            flight_id = self.get_valid_input(
                prompt="What is the ID of the flight that you want to remove the pilot from?",
                is_valid=lambda x : x.isdigit() and self.db.flights.exists(x),
                error_message="Flight ID's must be a non negative integer and must exist in the database."
            )
            if flight_id is None:
                return

            pilot_id = self.get_valid_input(
                prompt="What is the ID of the pilot that you want to remove from this flight?",
                is_valid=lambda x : x.isdigit() and self.db.pilots.exists(x),
                error_message="Pilot ID's must be a non negative integer and must exist in the database."
            )
            if pilot_id is None:
                return

            # the pilot must be on the flight for them to be removed
            if not self.db.flight_pilots.exists(flight_id, pilot_id): 
                print("That pilot is not on that flight. Press Enter to go back to the delete menu.")
                self.get_input()
                return

            remaining_rows = self.db.flight_pilots.delete_and_return(flight_id, pilot_id)
            print("Successfully removed pilot from flight. Here are the remaining pilots of this flight:") 
        elif option == "8": # remove a customer
            flight_id = self.get_valid_input(
                prompt="What is the ID of the flight that you want to remove the customer from?",
                is_valid=lambda x : x.isdigit() and self.db.flights.exists(x),
                error_message="Flight ID's must be a non negative integer and must exist in the database."
            )
            if flight_id is None:
                return

            customer_id = self.get_valid_input(
                prompt="What is the ID of the customer that you want to remove from this flight?",
                is_valid=lambda x : x.isdigit() and self.db.customers.exists(x),
                error_message="Customer ID's must be a non negative integer and must exist in the database."
            )
            if customer_id is None:
                return

            # the customer must be on the flight for them to be removed
            if not self.db.flight_passengers.exists(flight_id, customer_id):
                print("That customer is not on that flight. Press Enter to go back to the delete menu.")
                self.get_input()
                return

            remaining_rows = self.db.flight_passengers.delete_and_return(flight_id, customer_id)
            print("Successfully removed customer from flight. Here are the remaining customers of this flight:") 

        self.start_paginator_from_rows(remaining_rows) # start paginator using the remaining_rows