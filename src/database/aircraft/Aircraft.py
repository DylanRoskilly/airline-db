class Aircraft:
    def __init__(
        self, 
        aircraft_id: int,
        name: str, 
        type: int, 
        max_passengers: int
    ) -> None:
        self.aircraft_id = aircraft_id
        self.name = name
        self.type = type
        self.max_passengers = max_passengers

    def get_column_names(self) -> list[str]:
        return ["Aircraft ID", "Name", "Type", "Max Passengers"]

    def to_row(self) -> list[str]:
        return [str(self.aircraft_id), self.name, "Helicopter" if int(self.type) == 2 else "Plane", str(self.max_passengers)]