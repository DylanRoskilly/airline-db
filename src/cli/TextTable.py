class TextTable:
    def __init__(self, column_names: list[str]) -> None:
        self.column_names = column_names
        self.num_of_columns = len(column_names)

        self.rows = []
    
    def add_row(self, row: list[str]) -> 'TextTable': 
        if self.num_of_columns != len(row):
            raise Exception("Trying to add a row to a TextTable whose length is not equal to the number of columns") 

        self.rows.append(row)

        return self
    
    # gets a string to output the TextTable
    def get_string(self) -> str:
        column_widths = [] # stores the maximum widths for each column 
        all_rows = [self.column_names] + self.rows 
        for c in range(self.num_of_columns):
            cur_max = -1
            for r in range(len(all_rows)):
                cur_max = max(cur_max, len(all_rows[r][c])) # get the maximum width
            column_widths.append(cur_max)
        
        # generate the bar to separate rows
        row_bar = "+"
        for width in column_widths:
            row_bar += "-" * width + "+"
            
        output = [row_bar]

        for r in range(len(all_rows)):
            row = "|"
            for c in range(self.num_of_columns):
                # calculates the required number of padding
                row += all_rows[r][c] + (" " * (column_widths[c] - len(all_rows[r][c]))) + "|" 
            output.append(row)
            if r == 0: # add a bar under the column names
                output.append(row_bar)
        output.append(row_bar)

        return "\n".join(output)