import datetime

# determine if a date is in the format YYYY-MM-DD 
# also checks that DD is valid for MM. e.g. DD cannot be 30 if MM is 2. 
def validate_date(date: str) -> bool:
    if len(date) != 10:
        return False

    try:
        datetime.date.fromisoformat(date)
    except ValueError:
        return False
    else:
        return True
        
# determine if a date and time is in the format YYYY-MM-DD HH:MM:SS
# also checks that 0 <= HH < 60 etc...
def validate_date_time(date_time: str) -> bool:
    if len(date_time) != 19:
        return False

    try:
        datetime.datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return False
    else:
        return True