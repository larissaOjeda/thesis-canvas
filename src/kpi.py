from sqlalchemy.orm import Session
from sqlalchemy import text
from db_config import SessionManager

# def calculate_course_requirements_progress(session: Session):
#     query = text("""
#         WITH progress_data AS (
#             SELECT
#                 course_id,
#                 user_id,
#                 COUNT(CASE WHEN requirements_met::jsonb @> '[{"type":"must_view"}]' THEN 1 END) AS completed_requirements,
#                 COUNT(*) AS total_requirements
#             FROM
#                 context_module_progressions
#             GROUP BY
#                 course_id, user_id
#         )
#         SELECT
#             course_id,
#             ROUND(CAST(AVG(completed_requirements::FLOAT / total_requirements * 100) AS numeric), 2) AS progress_percentage
#         FROM
#             progress_data
#         GROUP BY
#             course_id;
#     """)
#     result = session.execute(query)
#     return result.fetchall()



# if __name__ == "__main__":
#     with SessionManager() as session:
#         detailed_progress = calculate_course_requirements_progress(session)
#         for module_progress in detailed_progress:
#             # Access by index (0 for context_module_id, 1 for progress_percentage)
#             print(f"Module {module_progress[0]}: {module_progress[1]}%")

from sqlalchemy import text
from sqlalchemy.orm import Session
from db_config import SessionManager

def calculate_course_requirements_progress(session: Session):
    query = text("""
        WITH progress_data AS (
            SELECT
                context_module_id,
                user_id,
                COUNT(CASE WHEN requirements_met::jsonb @> '[{"type":"must_view"}]' THEN 1 END) AS completed_requirements,
                COUNT(*) AS total_requirements
            FROM
                context_module_progressions
            GROUP BY
                context_module_id,
                user_id
        )
        SELECT
            context_module_id,
            ROUND(CAST(AVG(completed_requirements::FLOAT / total_requirements * 100) AS numeric), 2) AS progress_percentage
        FROM
            progress_data
        GROUP BY
            context_module_id;
    """)
    result = session.execute(query)
    return result.fetchall()


if __name__ == "__main__":
    with SessionManager() as session:
        results = calculate_course_requirements_progress(session)
        for course_id, progress in results:
            print(f"Course {course_id}: {progress}% complete")
