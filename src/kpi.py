from sqlalchemy import text
from db_config import SessionManager
from queries import (
    get_progress_in_course_requirements_query, 
    get_feedback_time_by_course_query, 
    get_course_completion_rate_query, 
    get_learning_objective_completion_query, 
    get_course_retention_query,
)

# KPI 1
def execute_module_completion_query(start_date: str, end_date: str):
    results = []
    MODULE_COMPLETION_BY_COURSE = get_progress_in_course_requirements_query(start_date, end_date)

    with SessionManager() as session:
        query = session.execute(text(MODULE_COMPLETION_BY_COURSE))
        results = query.fetchall()

    return results

# TODO: ADD KPI 2 (kpi and query are designed) but I have not been able to download the web_logs table

# KPI 3
def execute_avg_feedback_time_by_course_query(start_date: str, end_date: str):
    results = []
    FEEDBACK_TIME_BY_COURSE = get_feedback_time_by_course_query(start_date, end_date)

    with SessionManager() as session:
        query = session.execute(text(FEEDBACK_TIME_BY_COURSE))
        results = query.fetchall()

    return results

# KPI 4
def execute_course_completion_rate_query(start_date: str, end_date: str):
    results = []
    COURSE_COMPLETION_RATE = get_course_completion_rate_query(start_date, end_date)

    with SessionManager() as session:
        query = session.execute(text(COURSE_COMPLETION_RATE))
        results = query.fetchall()

    return results

# KPI 5
def execute_learning_objective_completion_query(start_date: str, end_date: str):
    results = []
    LEARNING_OBJECTIVES_COMPLETION = get_learning_objective_completion_query(start_date, end_date)

    with SessionManager() as session:
        query = session.execute(text(LEARNING_OBJECTIVES_COMPLETION))
        results = query.fetchall()

    return results


# KPI 6
def execute_student_retention_rate_query(start_date: str, end_date: str):
    results = []
    STUDENT_RETENTION_RATE = get_course_retention_query(start_date, end_date)

    with SessionManager() as session:
        query = session.execute(text(STUDENT_RETENTION_RATE))
        results = query.fetchall()

    return results


if __name__ == "__main__":
    start_date = '2024-01-01'
    end_date = '2024-06-01'
    
    # results = execute_module_completion_query(start_date, end_date)
    # for course_id, progress in results:
    #         print(f"Course {course_id} had an overall module completion of {progress}%")
    
    # results_3 = execute_avg_feedback_time_by_course_query(start_date, end_date)
    # for course_id, progress in results_3:
    #     print(f"Course {course_id}: {progress} avg feedback time")

    # TODO: Add results_2 (kpi and query are designed) but I have not been able to download the web_logs table

    # results_4 = execute_course_completion_rate_query(start_date, end_date)
    # for course_id, total_enrolled, completed_count, completion_rate in results_4: 
    #     print(f"Course {course_id}, total enrolled {total_enrolled}, completed count = {completed_count}, rate is {completion_rate}")

    # TODO: Revise the query cause its prompting only a few little results  
    results_5 = execute_learning_objective_completion_query(start_date, end_date)
    print(results_5)

    # TODO: Revise the query cause its prompting 100 or 0 as rate for all values 
    # results_6 = execute_student_retention_rate_query(start_date, end_date)
    # for course_id, course_name, intial_en, final_en, rate in results_6:
    #     print(course_id, rate)
    

   