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



def calculate_monthly_course_availability(courses_df, year, semester):
    """
    Calculates the monthly counts of active and inactive courses for a given semester.

    Args:
        courses_df (pd.DataFrame): DataFrame containing course information.
        year (int): Year of the semester.
        semester (str): Semester name ('spring', 'summer', or 'winter').

    Returns:
        dict: Dictionary with months as keys and two lists, 'active' and 'inactive', containing monthly counts.
    """
    start_semester, end_semester = get_semester_dates(year, semester)

    # Convert course dates to UTC
    courses_df['start_at'] = pd.to_datetime(courses_df['value.created_at'], utc=True)
    courses_df['end_at'] = pd.to_datetime(courses_df['value.updated_at'], utc=True)

    # Define months based on semester
    if semester.lower() == 'spring':
        months = ['January', 'February', 'March', 'April', 'May', 'June']
    elif semester.lower() == 'summer':
        months = ['June', 'July']
    elif semester.lower() == 'winter':
        months = ['August', 'September', 'October', 'November', 'December']

    active_counts = []
    inactive_counts = []

    # Calculate active and inactive course counts for each month
    for month in months:
        month_start = pd.Timestamp(f"{year}-{month}-01", tz='UTC')
        month_end = month_start + pd.offsets.MonthEnd(1)

        # Active courses for the month
        active_courses = courses_df[
            (courses_df['value.workflow_state'] == 'available') &
            (courses_df['start_at'] <= month_end) &
            ((courses_df['end_at'] >= month_start) | courses_df['end_at'].isna())
        ]

        # Inactive courses for the month
        inactive_courses = courses_df[
            (courses_df['value.workflow_state'] != 'available') &
            (courses_df['start_at'] <= month_end) &
            (courses_df['end_at'] < month_start) &
            courses_df['end_at'].notna()
        ]

        active_counts.append(active_courses.shape[0])
        inactive_counts.append(inactive_courses.shape[0])

    return {'month': months, 'active': active_counts, 'inactive': inactive_counts}


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

def calculate_feedback_time_vs_assignment_count(submissions_df, year, semester):
    # Convert dates to datetime
    submissions_df['value.created_at'] = pd.to_datetime(submissions_df['value.created_at'], utc=True)
    submissions_df['value.updated_at'] = pd.to_datetime(submissions_df['value.updated_at'], utc=True)

    # Get semester start and end dates
    start_date, end_date = get_semester_dates(year, semester)

    # Filter submissions by semester
    filtered_submissions = submissions_df[
        (submissions_df['value.created_at'] >= start_date) & 
        (submissions_df['value.created_at'] <= end_date)
    ]

    # Calculate feedback time in hours
    filtered_submissions['feedback_time'] = (
        filtered_submissions['value.updated_at'] - filtered_submissions['value.created_at']
    ).dt.total_seconds() / 3600

    # Remove rows with NaN feedback times
    filtered_submissions = filtered_submissions.dropna(subset=['feedback_time'])

    # Calculate average feedback time per course
    avg_feedback_time_per_course = filtered_submissions.groupby('value.course_id')['feedback_time'].mean().reset_index()
    avg_feedback_time_per_course.columns = ['value.course_id', 'average_feedback_time']

    # Calculate the number of assignments per course
    assignment_count_per_course = filtered_submissions.groupby('value.course_id').size().reset_index(name='assignment_count')

    # Merge the two results to have both average feedback time and assignment count per course
    feedback_time_vs_assignment_count = avg_feedback_time_per_course.merge(
        assignment_count_per_course, on='value.course_id'
    )

    return feedback_time_vs_assignment_count


def courses_with_high_failing_enrollments(
    enrollments_df,
    scores_df,
    year,
    semester,
    failing_threshold=60,
    fail_count_threshold=10  
):
    # Convert dates to datetime
    enrollments_df['value.created_at'] = pd.to_datetime(enrollments_df['value.created_at'], utc=True)
    scores_df['value.created_at'] = pd.to_datetime(scores_df['value.created_at'], utc=True)
    

    # Get semester dates
    start_date, end_date = get_semester_dates(year, semester)
    semester_start = pd.to_datetime(start_date)
    semester_end = pd.to_datetime(end_date)
    
    # Filter enrollments during the semester
    semester_enrollments = enrollments_df[
        (enrollments_df['value.created_at'] >= semester_start) &
        (enrollments_df['value.created_at'] <= semester_end) &
        (enrollments_df['value.workflow_state'] == 'available')
    ]
    # Merge enrollments with scores
    merged_df = semester_enrollments.merge(
        scores_df[['value.enrollment_id', 'value.final_score']],
        left_on='key.id',  # Enrollment ID in enrollments_df
        right_on='value.enrollment_id',  # Enrollment ID in scores_df
        how='left'
    )

    # Identify failing enrollments
    failing_enrollments = merged_df[
        (merged_df['value.final_score'] < failing_threshold) |
        (merged_df['value.final_score'].isnull())  # Assuming null scores are failing
    ]

    # Count failing enrollments per course
    failing_counts = failing_enrollments.groupby('value.enrollment_id').size().reset_index(name='failing_enrollments')
    
    # Identify courses exceeding the failing enrollment threshold
    flagged_courses = failing_counts[
        failing_counts['failing_enrollments'] >= fail_count_threshold
    ]
    
    return flagged_courses



def calculate_average_assignment_score(assignments_df, submissions_df):
    """
    Calculates the average assignment score per course.
    
    Handles NaN values by excluding them from the calculation.
    """
    # Ensure correct data types
    assignments_df['key.id'] = assignments_df['key.id'].astype(int)
    assignments_df['value.context_id'] = assignments_df['value.context_id'].astype(int)
    submissions_df['value.assignment_id'] = submissions_df['value.assignment_id'].astype(int)
    submissions_df['value.score'] = pd.to_numeric(submissions_df['value.score'], errors='coerce')
    
    # Merge DataFrames on assignment IDs
    merged_df = pd.merge(
        submissions_df,
        assignments_df[['key.id', 'value.context_id']],
        left_on='value.assignment_id',
        right_on='key.id',
        how='inner'
    )
    
    # Drop rows with NaN scores
    merged_df = merged_df.dropna(subset=['value.score'])
    
    # Calculate average score per course
    average_scores = merged_df.groupby('value.context_id')['value.score'].mean().reset_index()
    average_scores['value.context_id'] = average_scores['value.context_id'].astype(str)
    average_scores.rename(columns={'value.context_id': 'course_id'}, inplace=True)
    
    return average_scores