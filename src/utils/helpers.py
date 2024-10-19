import pandas as pd 

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

