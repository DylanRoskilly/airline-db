class Pilot:
    def __init__(
        self, 
        pilot_id: str,
        first_name: str, 
        last_name: str, 
        date_of_birth: str
    ) -> None:
        self.pilot_id = pilot_id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
    
    def get_column_names(self) -> list[str]:
        return ["Pilot ID", "First Name", "Last Name", "Date of Birth"]

    def to_row(self) -> list[str]:
        return [str(self.pilot_id), self.first_name, self.last_name, self.date_of_birth]