from utils.helpers import get_semester_dates
import pandas as pd


def create_ratio_of_course_availability_and_activity_for_semester(courses_df, year, semester):
    start_semester, end_semester = get_semester_dates(year, semester)

    # Convert course dates to UTC
    courses_df['start_at'] =  pd.to_datetime(courses_df['value.created_at'], utc=True)
    courses_df['end_at'] = pd.to_datetime(courses_df['value.updated_at'], utc=True)

    # Filter active courses within the semester
    active_courses = courses_df[
        (courses_df['value.workflow_state'] == 'available') &
        (courses_df['start_at'] <= end_semester) &
        ((courses_df['end_at'] >= start_semester) | courses_df['end_at'].isna())
    ]

    # Filter inactive courses within the semester
    inactive_courses = courses_df[
        (courses_df['value.workflow_state'] != 'available') &
        (courses_df['start_at'] <= end_semester) &
        (courses_df['end_at'] < start_semester) & 
        courses_df['end_at'].notna()  # Ensure the course has ended
    ]

    # Calculate counts
    active_count = active_courses.shape[0]
    inactive_count = inactive_courses.shape[0]

    # Calculate ratio of active to inactive courses
    if inactive_count > 0:
        ratio_active_to_inactive = active_count / inactive_count
    else:
        ratio_active_to_inactive = float('inf')

    return active_count, inactive_count, ratio_active_to_inactive



def create_student_retention_rate(enrollments_df, year, semester):
    start_semester, end_semester = get_semester_dates(year, semester)

    enrollments_df['created_at'] = pd.to_datetime(enrollments_df['value.created_at'], utc=True)
    enrollments_df['updated_at'] = pd.to_datetime(enrollments_df['value.updated_at'],  utc=True)
    
    # Step 1: Initial Enrollment (students active at the start of the semester)
    initial_enrollment = enrollments_df[
        (enrollments_df['created_at'] <= start_semester) & 
        (enrollments_df['value.workflow_state'] == 'available')  
    ].shape[0]

    # Step 2: Final Enrollment (students still active at the end of the semester)
    final_enrollment = enrollments_df[
        (enrollments_df['updated_at'] >= end_semester) & 
        (enrollments_df['value.workflow_state'] == 'available')
    ].shape[0]

    # Step 3: Calculate the Retention Rate
    if initial_enrollment > 0:
        retention_rate = (final_enrollment / initial_enrollment) * 100
    else:
        retention_rate = 0

    return retention_rate


def calculate_tasks_completion_rate(assignments_df, submissions_df, year, semester):
    start_semester, end_semester = get_semester_dates(year, semester)

    assignments_df['created_at'] = pd.to_datetime(assignments_df['value.created_at'], utc=True)
    submissions_df['submitted_at'] = pd.to_datetime(submissions_df['value.submitted_at'], utc=True)

    # Filter assignments within the semester
    assignments_in_semester = assignments_df[
        (assignments_df['created_at'] >= start_semester) &
        (assignments_df['created_at'] <= end_semester)
    ]

    # Filter submissions within the semester
    submissions_in_semester = submissions_df[
        (submissions_df['submitted_at'] >= start_semester) &
        (submissions_df['submitted_at'] <= end_semester) &
        (submissions_df['value.workflow_state'] == 'graded')
    ]

    # Calculate total number of assignments assigned in the semester
    total_assignments = assignments_in_semester['key.id'].nunique()

    if total_assignments == 0:
        return 0.0

    # Calculate completion rate (unique assignment IDs in submissions / total assignments)
    completed_tasks = submissions_in_semester['value.assignment_id'].nunique()
    completion_rate = (completed_tasks / total_assignments) * 100

    return completion_rate


def calculate_average_score(scores_df, year, semester):
    start_semester, end_semester = get_semester_dates(year, semester)

    scores_df['value.updated_at'] = pd.to_datetime(scores_df['value.updated_at'])

    filtered_scores = scores_df[
        (scores_df['value.updated_at'] >= start_semester) & 
        (scores_df['value.updated_at'] <= end_semester) & 
        (scores_df['value.workflow_state'] == 'active')  # Consider only active scores
    ]

    if filtered_scores.empty:
        return 0.0

    average_score = filtered_scores['value.current_score'].mean()
    return average_score


def calculate_score_distribution(scores_df, year, semester):

    scores_df['value.created_at'] = pd.to_datetime(scores_df['value.created_at'], errors='coerce')
    scores_df['value.updated_at'] = pd.to_datetime(scores_df['value.updated_at'], errors='coerce')
    scores_df = scores_df.dropna(subset=['value.created_at'])

    start_date, end_date = get_semester_dates(year, semester)

    filtered_scores = scores_df[
        (scores_df['value.created_at'] <= end_date) &   
        ((scores_df['value.updated_at'] >= start_date) |
         (scores_df['value.updated_at'].isna()))  
    ]

    scores = filtered_scores['value.final_score'].dropna()

    return scores
