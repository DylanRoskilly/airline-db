from typing import Callable
from cli.TextTable import TextTable

# a base class that represents a table in the database
# it is inherited and functions are added to insert, delete, etc from a specific table
# see AircraftsTable.py for more information
class Table:
    def __init__(self, database: 'Database'):
        self.db = database
    
    # creates a string that allows the user to input an integer to select a column in this table
    # returns (x, y) where x is a list of the names of the columns and y is this output string
    # the all_columns parameters determines if it should return all columns or only columns that are settable
    def get_column_choices(self, all_columns: bool = True) -> (list[str], str):
        choice = 1
        column_names = []
        output = ""

        for column in self.columns:
            if all_columns or self.columns[column].settable:
                output += f"\n    {choice}. {column}"
                column_names.append(column)
                choice += 1
        
        return (column_names, output)

# represents a column in a table
# every Table class should contain a columns property that contains a dictionary of Columns
class Column:
    def __init__(
        self, 
        name: str, 
        settable: bool, 
        is_valid: Callable[str, bool], 
        validation_prompt: str, 
        insert_prompt: str = None, 
        update_prompt: str = None
    ):
        self.name = name # name of the column in snake_case

        self.settable = settable # whether the column can be set and updated by the user
        self.insert_prompt = insert_prompt # what to show the user to get them to insert a value into this column
        self.update_prompt = update_prompt # what to show the user to get them to update a value in this column
        
        self.is_valid = is_valid # function to determine if a value meets the validation requirements of this column
        self.validation_prompt = validation_prompt + "." # what to show the user if their input is invalid