import math
from cli.TextTable import TextTable

class Paginator:
    def __init__(self, text_table):
        self.text_table = text_table
        self.cur_page = -1 # 0-indexed
        self.num_of_pages = math.ceil(len(self.text_table.rows) / 5) # each page has 5 rows max
    
    # gets a string to output the current page
    def get_string(self) -> str:
        page_table = TextTable(self.text_table.column_names)
        # min(x, y) is used as there could be less than 5 rows remaining
        for i in range(self.cur_page*5, min((self.cur_page+1)*5, len(self.text_table.rows))):
            page_table.add_row(self.text_table.rows[i])
        
        output = page_table.get_string()
        if self.is_last_page():
            output += f"\nPage {self.cur_page+1} of {self.num_of_pages}. Press Enter to go back to the menu."
        else:
            output += f"\nPage {self.cur_page+1} of {self.num_of_pages}. Press Enter to go to the next page. Input 0 to go back to the menu."

        return output

    def next_page(self) -> str:
        self.cur_page += 1
        return self.get_string()

    # determines if we're on the last page
    def is_last_page(self) -> bool:
        return self.cur_page+1 >= self.num_of_pages

    # begin the paginator 
    def start(self) -> None: 
        if self.num_of_pages < 1:
            print("Page 0 of 0. No results. Press Enter to go back to the menu.")
            input(">> ")
            return

        print(self.next_page())
        option = input(">> ")
        # stop if the user input is 0 or if its the last page
        while option != "0" and not self.is_last_page(): 
            print(self.next_page())
            option = input(">> ")