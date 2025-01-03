from datetime import timedelta

NAMESPACE="canvas"
APP_NAME="thesis-canvas"
DEFAULT_STATEMENT_TIMEOUT = timedelta(seconds=90)   # 1.5 mins 


# Folder paths
TABLE_SCHEMAS_PATH="/Users/larissatrasvina/thesis-canvas/src/table_schemas"
CSV_FOLDER_PATH="/Users/larissatrasvina/thesis-canvas/src/csv_files"

# CSV file paths 
COURSES_PATH="/Users/larissatrasvina/thesis-canvas/src/csv_files/courses.csv"
ENROLLMENTS_PATH="/Users/larissatrasvina/thesis-canvas/src/csv_files/enrollments.csv"
ASSIGNMENTS_PATH ="/Users/larissatrasvina/thesis-canvas/src/csv_files/assignments.csv"
SUBMISSIONS_PATH="/Users/larissatrasvina/thesis-canvas/src/csv_files/submissions.csv"
SCORES_PATH="/Users/larissatrasvina/thesis-canvas/src/csv_files/scores.csv"
USERS_PATH="/Users/larissatrasvina/thesis-canvas/src/csv_files/users.csv"
CONTEXT_MODULES="/Users/larissatrasvina/thesis-canvas/src/csv_files/context_modules.csv"
COURSE_SECTIONS="/Users/larissatrasvina/thesis-canvas/src/csv_files/course_sections.csv"


TABLE_NAMES = []
TABLES_FOR_KPIS_IN_CANVAS_LOGS = ["web_logs"]


TABLES_FOR_KPIS_IN_CANVAS = [
    # Tables for Course Requirements Progress
    "context_module_progressions",
    "context_modules",
    
    # tables for Average Feedback Time
    "submissions",
    "submission_comments",
    
    # tables for Course Completion Rate
    "enrollments",
    
    # tables for Learning Objectives
    "learning_outcome_results",
    "learning_outcomes",
    
    # Common/Core tables
    "courses",
    "users",
    
    # Reference tables
    "enrollment_terms",
    "course_sections",
    "roles",
    "conversations",
]

