from typing import Callable, Iterator
from cli.TextTable import TextTable
from cli.Paginator import Paginator

# base class representing a menu
# each menu will inherit this class and add their own print_menu() and respond()
class Menu:
    def __init__(self, database):
        self.db = database

        # standard options that have a table representing them
        self.options = ["pilots", "customers", "aircrafts", "airports", "terminals", "flights"] 

    # shows a prompt and returns the user input
    def get_input(self) -> str:
        return input(">> ")
    
    def start(self) -> None:
        self.print_menu()

        option = self.get_input()
        while option != "0": # keep showing menu options until 0 is entered
            # each superclass should have a function defined 
            # called respond that responds to the inputted option
            self.respond(option)

            self.print_menu()
            option = self.get_input()
    
    # get a valid input from the user
    # is_valid determines if the user input is valid
    # prompt is shown to the user to get their input
    # error_message is shown if the input is invalid
    def get_valid_input(self, is_valid: Callable[str, bool], prompt: str, error_message: str) -> str:
        prompt += "\nInput \"q!\" to go back to the menu."
        error_message = f"Invalid Input. Try again: {error_message}\nInput \"q!\" to go back to the menu."

        print(prompt)
        user_input = self.get_input() 
        if user_input == "q!": # stop if q! is entered
            return

        while not is_valid(user_input): # keep prompting until a valid input is entered
            print(error_message)
            user_input = self.get_input()
            if user_input == "q!": # stop if q! is entered
                return
        
        return user_input 

    # a 'Row' is an object representing a row. e.g. Aircraft, ExtendedFlight
    def start_paginator_from_rows(self, rows: Iterator['Row'] | None) -> None:
        if rows is None:
            print("No rows. Press Enter to go back to the menu.")
            self.get_input()
            return

        # rows is an iterator so we cannot access the first element directly. 
        # must loop through the iterator to get the first element
        first = True 
        text_table = None 
        
        for row in rows: # loop through all rows and add them to the text table
            if first:
                text_table = TextTable(row.get_column_names()) # create the text table from the first row
                first = False

            text_table.add_row(row.to_row())
        
        if text_table is None:
            print("No rows. Press Enter to go back to the menu.")
            self.get_input()
            return
        
        paginator = Paginator(text_table)
        paginator.start()
