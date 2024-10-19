from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Select, HoverTool
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column, row

from utils.helpers import get_semester_dates
from utils.constants import COURSES_PATH, ENROLLMENTS_PATH, ASSIGNMENTS_PATH, SUBMISSIONS_PATH

import pandas as pd

courses_df = pd.read_csv(COURSES_PATH)
enrollments_df = pd.read_csv(ENROLLMENTS_PATH)
assignments_df = pd.read_csv(ASSIGNMENTS_PATH)
submissions_df =  pd.read_csv(SUBMISSIONS_PATH)

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


def calculate_completion_rate(assignments_df, submissions_df, year, semester):
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

# Initial plot data for Spring 2024
year = 2024
semester = 'Spring'
active_count, inactive_count, ratio = create_ratio_of_course_availability_and_activity_for_semester(courses_df, year, semester)
retention_rate = create_student_retention_rate(enrollments_df, year, semester)
completion_rate = calculate_completion_rate(assignments_df, submissions_df, year, semester)

# Data sources for the plots
course_source = ColumnDataSource(data=dict(categories=['Active', 'Inactive'], counts=[active_count, inactive_count]))
retention_source = ColumnDataSource(data=dict(start=[0], end=[retention_rate / 100 * 2 * 3.14159], retention=[retention_rate]))  # Added 'retention'
retention_text_source = ColumnDataSource(data=dict(rate_text=[f"{retention_rate:.1f}%"]))
completion_source = ColumnDataSource(data=dict(start=[0], end=[completion_rate / 100 * 2 * 3.14159], completion=[completion_rate]))  # Added 'completion'
completion_text_source = ColumnDataSource(data=dict(rate_text=[f"{completion_rate:.1f}%"]))

# Create Course Availability plot
course_plot = figure(x_range=['Active', 'Inactive'], height=350, title="Course Availability", toolbar_location=None)
course_plot.vbar(x='categories', top='counts', width=0.9, source=course_source)
retention_plot = figure(width=350, height=350, title="Student Retention Rate", toolbar_location=None, x_range=(-1, 1), y_range=(-1, 1))
retention_plot.annular_wedge(x=0, y=0, inner_radius=0.4, outer_radius=0.9, start_angle='start', end_angle='end', source=retention_source, color="blue")
retention_plot.text(x=0, y=0, text='rate_text', text_align="center", text_baseline="middle", text_font_size="20pt", source=retention_text_source)

# Create Completion Rate plot using Annular Wedge
completion_plot = figure(width=350, height=350, title="Assignment Completion Rate", toolbar_location=None, x_range=(-1, 1), y_range=(-1, 1))
completion_plot.annular_wedge(x=0, y=0, inner_radius=0.4, outer_radius=0.9, start_angle='start', end_angle='end', source=completion_source, color="green")
completion_plot.text(x=0, y=0, text='rate_text', text_align="center", text_baseline="middle", text_font_size="20pt", source=completion_text_source)

# Add hover for Course Availability
hover_course = HoverTool()
hover_course.tooltips = [("Category", "@categories"), ("Count", "@counts")]
course_plot.add_tools(hover_course)

# Add hover for Retention Rate (using the 'retention' field)
hover_retention = HoverTool()
hover_retention.tooltips = [("Retention Rate", "@retention{0.0}%")]
retention_plot.add_tools(hover_retention)

# Add hover for Completion Rate (using the 'completion' field)
hover_completion = HoverTool()
hover_completion.tooltips = [("Completion Rate", "@completion{0.0}%")]
completion_plot.add_tools(hover_completion)

# Dropdown widgets for year and semester
semester_select = Select(title="Semester", value="Spring", options=["Spring", "Summer", "Winter"])
year_select = Select(title="Year", value="2024", options=[str(x) for x in range(2021, 2025)])

# Update function for all plots
def update_plots(attr, old, new):
    selected_year = int(year_select.value)
    selected_semester = semester_select.value

    # Update course availability data
    active_count, inactive_count, ratio = create_ratio_of_course_availability_and_activity_for_semester(courses_df, selected_year, selected_semester)
    course_source.data = dict(categories=['Active', 'Inactive'], counts=[active_count, inactive_count])

    # Update student retention rate data
    retention_rate = create_student_retention_rate(enrollments_df, selected_year, selected_semester)
    retention_source.data = dict(start=[0], end=[retention_rate / 100 * 2 * 3.14159], retention=[retention_rate])  # Update 'retention' field
    retention_text_source.data = dict(rate_text=[f"{retention_rate:.1f}%"])

    # Update assignment completion rate data
    completion_rate = calculate_completion_rate(assignments_df, submissions_df, selected_year, selected_semester)
    completion_source.data = dict(start=[0], end=[completion_rate / 100 * 2 * 3.14159], completion=[completion_rate])  # Update 'completion' field
    completion_text_source.data = dict(rate_text=[f"{completion_rate:.1f}%"])

# Add callback for dropdowns
semester_select.on_change('value', update_plots)
year_select.on_change('value', update_plots)

# Layout for the dashboard with plot labels
dashboard_layout = column(row(year_select, semester_select), row(course_plot, retention_plot, completion_plot))

# Add the layout to the current document
# To run this project use "bokeh serve --show kpi_calculator.py"
curdoc().add_root(dashboard_layout)
curdoc().title = "Course Availability, Retention, and Completion Dashboard"

