import pandas as pd 
from datetime import datetime


def get_semester_dates(year, semester):
    """
    Returns the start and end date of the semester based on the given year and semester type, respecting UTC time.
    Semesters:
    - Spring: January to June
    - Summer: June to July
    - Winter: August to December
    """
    if semester == 'Spring':
        return pd.Timestamp(f'{year}-01-01', tz='UTC'), pd.Timestamp(f'{year}-06-30', tz='UTC')
    elif semester == 'Summer':
        return pd.Timestamp(f'{year}-06-01', tz='UTC'), pd.Timestamp(f'{year}-07-31', tz='UTC')
    elif semester == 'Winter':
        return pd.Timestamp(f'{year}-08-01', tz='UTC'), pd.Timestamp(f'{year}-12-31', tz='UTC')
    else:
        raise ValueError("Invalid semester. Choose between 'Spring', 'Summer', or 'Winter'.")


def get_semester_months(year, semester):
    if semester == "Spring":
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 6, 30)
    elif semester == "Summer":
        start_date = datetime(year, 6, 1)
        end_date = datetime(year, 8, 31)
    elif semester == "Fall":
        start_date = datetime(year, 9, 1)
        end_date = datetime(year, 12, 31)
    else:
        raise ValueError("Invalid semester")

    months = pd.date_range(start_date, end_date, freq='MS').strftime('%b').tolist()
    return months