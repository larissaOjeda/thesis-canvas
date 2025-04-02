from datetime import timedelta

NAMESPACE="canvas"
APP_NAME="thesis-canvas"
DEFAULT_STATEMENT_TIMEOUT = timedelta(seconds=90)   # 1.5 mins 

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

