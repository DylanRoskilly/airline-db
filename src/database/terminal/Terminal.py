class Terminal:
    def __init__(
        self, 
        terminal_id: int,
        airport_id: int,
        name: str
    ) -> None:
        self.terminal_id = terminal_id
        self.airport_id = airport_id
        self.name = name
    
    def get_column_names(self) -> list[str]:
        return ["Terminal ID", "Airport ID", "Name"]
        
    def to_row(self) -> list[str]:
        return [str(self.terminal_id), str(self.airport_id), self.name]

class ExtendedTerminal:
    def __init__(
        self, 
        terminal_id: int,
        terminal_name: str,
        airport_id: int,
        airport_name: str,
        airport_address: str
    ) -> None:
        self.terminal_id = terminal_id
        self.terminal_name = terminal_name
        self.airport_id = airport_id
        self.airport_name = airport_name
        self.airport_address = airport_address
    
    def get_column_names(self) -> list[str]:
        return ["Terminal ID", "Terminal Name", "Airport ID", "Airport Name", "Airport Address"]
        
    def to_row(self) -> list[str]:
        return [str(self.terminal_id), self.terminal_name, str(self.airport_id), self.airport_name, self.airport_address]
