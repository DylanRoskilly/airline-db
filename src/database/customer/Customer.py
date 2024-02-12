class Customer:
    def __init__(
        self, 
        customer_id: str,
        first_name: str, 
        last_name: str, 
        date_of_birth: str,
        home_address: str,
        phone_number: str
    ) -> None:
        self.customer_id = customer_id
        self.first_name = first_name
        self.last_name = last_name
        self.date_of_birth = date_of_birth
        self.home_address = home_address
        self.phone_number = phone_number
    
    def get_column_names(self) -> list[str]:
        return ["Customer ID", "First Name", "Last Name", "Date of Birth", "Home Address", "Phone Number"]
    
    def to_row(self) -> list[str]:
        return [str(self.customer_id), self.first_name, self.last_name, self.date_of_birth, self.home_address, self.phone_number]