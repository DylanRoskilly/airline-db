class FlightPilot:
    def __init__(
        self, 
        flight_id: int, 
        pilot_id: int
    ) -> None:
        self.flight_id = flight_id
        self.pilot_id = pilot_id
    
    def get_column_names(self) -> list[str]:
        return ["Flight ID", "Pilot ID"]

    def to_row(self) -> list[str]:
        return [str(self.flight_id), str(self.pilot_id)]