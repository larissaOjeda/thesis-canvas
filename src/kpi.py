from sqlalchemy import text
from db_config import SessionManager
import queries 
from utils import helpers
import pandas as pd
from datetime import datetime

# Helper function to save results to CSV
def save_to_csv(data, file_name):
    df = pd.DataFrame(data)
    df.to_csv(file_name, index=False)
    print(f"Saved {file_name}")


# KPI 1
def execute_module_completion_query(start_date: str, end_date: str):
    results = []
    MODULE_COMPLETION_BY_COURSE = queries.get_progress_in_course_requirements_query(start_date, end_date)

    with SessionManager() as session:
        query = session.execute(text(MODULE_COMPLETION_BY_COURSE))
        results = query.fetchall()

    return results

# KPI 3
def execute_avg_feedback_time_by_course_query(start_date: str, end_date: str):
    results = []
    FEEDBACK_TIME_BY_COURSE =queries.get_feedback_time_by_course_query(start_date, end_date)

    with SessionManager() as session:
        query = session.execute(text(FEEDBACK_TIME_BY_COURSE))
        results = query.fetchall()

    return results

# KPI 4
def execute_course_completion_rate_query(start_date: str, end_date: str):
    results = []
    COURSE_COMPLETION_RATE = queries.get_course_completion_rate_query(start_date, end_date)

    with SessionManager() as session:
        query = session.execute(text(COURSE_COMPLETION_RATE))
        results = query.fetchall()

    return results

# KPI 5
def execute_learning_objective_completion_query(start_date: str, end_date: str):
    results = []
    LEARNING_OBJECTIVES_COMPLETION = queries.get_learning_objective_completion_query(start_date, end_date)

    with SessionManager() as session:
        query = session.execute(text(LEARNING_OBJECTIVES_COMPLETION))
        results = query.fetchall()

    return results

# KPI 6
def execute_student_retention_rate_query(start_date: str, end_date: str, term_name: str):
    results = []
    STUDENT_RETENTION_RATE = queries.get_course_retention_query(start_date, end_date, term_name)

    with SessionManager() as session:
        query = session.execute(text(STUDENT_RETENTION_RATE))
        results = query.fetchall()

    return results

if __name__ == "__main__":
    now = datetime.now()
    year = now.year 
    semester = helpers.get_current_semester() 
    start_date, end_date = helpers.get_semester_dates(year, semester)

    # Option B) Manually change the dates of semesters 
    # start_date = "2024-01-01"
    # end_date = "2024-06-01"
    # semester = helpers.get_semester_term(start_date)
    
    # KPI 1
    module_completion_results = execute_module_completion_query(start_date, end_date)
    save_to_csv(module_completion_results, f"module_completion_{semester}_{year}.csv")

    # KPI 3
    feedback_time_results = execute_avg_feedback_time_by_course_query(start_date, end_date)
    save_to_csv(feedback_time_results, f"feedback_time_{semester}_{year}.csv")

    # KPI 4
    feedback_time_results = execute_course_completion_rate_query(start_date, end_date)
    save_to_csv(feedback_time_results, f"course_completion_rate_{semester}_{year}.csv")

    # KPI 5
    feedback_time_results = execute_learning_objective_completion_query(start_date, end_date)
    save_to_csv(feedback_time_results, f"learning_objective_completion_{semester}_{year}.csv")

    # KPI 6
    feedback_time_results = execute_student_retention_rate_query(start_date, end_date)
    save_to_csv(feedback_time_results, f"student_retention_rate_{semester}_{year}.csv")


   