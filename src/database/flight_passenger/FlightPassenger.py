class FlightPassenger:
    def __init__(
        self, 
        flight_id: int, 
        customer_id: int,
        seat_number: int,
    ) -> None:
        self.flight_id = flight_id
        self.customer_id = customer_id
        self.seat_number = seat_number
    
    def get_column_names(self) -> list[str]:
        return ["Flight ID", "Customer ID", "Seat Number"]

    def to_row(self) -> list[str]:
        return [str(self.flight_id), str(self.customer_id), str(self.seat_number)]