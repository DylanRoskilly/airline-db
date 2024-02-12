class Flight:
    def __init__(
        self, 
        flight_id: int,
        aircraft_id: int, 
        terminal_id: int, 
        destination: str, 
        boarding_time: str, 
        departure_time: str, 
        arrival_time: str
    ) -> None:
        self.flight_id = flight_id
        self.aircraft_id = aircraft_id
        self.terminal_id = terminal_id
        self.destination = destination
        self.boarding_time = boarding_time
        self.departure_time = departure_time
        self.arrival_time = arrival_time
    
    def get_column_names(self) -> list[str]:
        return ["Flight ID", "Aircraft ID", "Terminal ID", "Destination", "Boarding Time", "Departure Time", "Arrival Time"]
    
    def to_row(self) -> list[str]:
        return [str(self.flight_id), str(self.aircraft_id), str(self.terminal_id), self.destination, self.boarding_time, self.departure_time, self.arrival_time]

class ExtendedFlight:
    def __init__(
        self, 
        flight_id: int,
        aircraft_id: int, 
        aircraft_name: str, 
        terminal_id: int, 
        airport_name: str, 
        terminal_name: str, 
        destination: str, 
        boarding_time: str, 
        departure_time: str, 
        arrival_time: str
    ) -> None:
        self.flight_id = flight_id
        self.aircraft_id = aircraft_id
        self.aircraft_name = aircraft_name
        self.terminal_id = terminal_id
        self.airport_name = airport_name
        self.terminal_name = terminal_name
        self.destination = destination
        self.boarding_time = boarding_time
        self.departure_time = departure_time
        self.arrival_time = arrival_time
    
    def get_column_names(self) -> list[str]:
        return ["Flight ID", "Aircraft ID", "Aircraft Name", "Terminal ID", "Airport Name", "Terminal Name", "Destination", "Boarding Time", "Departure Time", "Arrival Time"]
    
    def to_row(self) -> list[str]:
        return [str(self.flight_id), str(self.aircraft_id), self.aircraft_name, str(self.terminal_id), self.airport_name, self.terminal_name, self.destination, self.boarding_time, self.departure_time, self.arrival_time]