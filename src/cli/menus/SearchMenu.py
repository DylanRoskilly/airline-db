from cli.menus.Menu import Menu
from cli.Paginator import Paginator
from cli.TextTable import TextTable

class SearchMenu(Menu):
    def print_menu(self) -> None: 
        print("""
+---------------------------------------------+
|                SEARCH MENU                  |
+---------------------------------------------+
|   1. Search for a pilot                     |
|   2. Search for a customer                  |
|   3. Search for an aircraft                 |
|   4. Search for an airport                  |
|   5. Search for a terminal                  |
|   6. Search for a flight                    |
|   7. Get the pilots controlling a flight    |
|   8. Get the passengers for a flight        |
|   0. Go back to the main menu               |
+---------------------------------------------+
        """)
    
    def respond(self, option: str) -> None:
        rows = None # initialise a variable that will store the rows returned from the search

        if option.isdigit() and 1 <= int(option) <= 6: # standard options
            table = getattr(self.db, self.options[int(option) - 1]) # get table for the inputted option
            
            option = self.get_valid_input(
                prompt="How do you want to search?\n    1. Get all rows in this table\n    2. Search using a specific column",
                is_valid=lambda x : x == "1" or x == "2",
                error_message="Must be 1 or 2."
            )
            if option is None:
                return
            elif option == "1":
                rows = table.get_all()
            else:
                # determine the column that the user wants to search by
                (column_names, options) = table.get_column_choices()
                option = self.get_valid_input(
                    prompt="What column do you want to search by?" + options,
                    is_valid=lambda x : x.isdigit() and 0 < int(x) <= len(column_names),
                    error_message=f"Must be an integer between 1 and {len(column_names)} inclusive."
                )                
                if option is None:
                    return
                
                column = table.columns[column_names[int(option)-1]] # get this Column from the table

                value = self.get_valid_input(
                    prompt="What's the value for the search in this column?",
                    is_valid=column.is_valid,
                    error_message=column.validation_prompt
                )                
                if value is None:
                    return
            
                rows = table.get(column.name, value)
        elif option == "7" or option == "8": # these two options are similar so combine them into one
            word = "pilots" if option == "7" else "passengers"

            flight_id = self.get_valid_input(
                prompt=f"What is the ID of the flight you want to get the {word} for?",
                is_valid=lambda x : x.isdigit() and self.db.flights.exists(x), 
                error_message="Flight ID must be a non negative integer and must exist in the database."
            )                
            if flight_id is None:
                return

            rows = self.db.flight_pilots.get(flight_id) if option == "7" else self.db.flight_passengers.get(flight_id)
              
        self.start_paginator_from_rows(rows) # begin paginator from returned rows