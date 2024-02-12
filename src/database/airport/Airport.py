class Airport:
    def __init__(
        self, 
        airport_id: int, 
        name: str, 
        address: str
    ) -> None:
        self.airport_id = airport_id
        self.name = name
        self.address = address
    
    def get_column_names(self) -> list[str]:
        return ["Airport ID", "Name", "Address"]
    
    def to_row(self) -> list[str]:
        return [str(self.airport_id), self.name, self.address]