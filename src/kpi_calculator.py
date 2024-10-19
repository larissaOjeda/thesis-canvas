from bokeh.io import curdoc
from bokeh.models import ColumnDataSource, Select, HoverTool
from bokeh.plotting import figure, output_file, save
from bokeh.layouts import column, row

from utils.helpers import get_semester_dates
from utils.constants import COURSES_PATH

import pandas as pd

courses_df = pd.read_csv(COURSES_PATH)

def create_course_availability_and_activity_for_semester(courses_df, year, semester):
    
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



# Create initial data for the plot (default to Spring 2024)
year = 2024
semester = 'Spring'
active_count, inactive_count, ratio = create_course_availability_and_activity_for_semester(courses_df, year, semester)

# Data source for Bokeh plot
source = ColumnDataSource(data=dict(categories=['Active', 'Inactive'], counts=[active_count, inactive_count]))

# Create bar chart
p = figure(x_range=['Active', 'Inactive'], height=350, title="Course Availability", toolbar_location=None)
p.vbar(x='categories', top='counts', width=0.9, source=source)

# Add interactive labels using HoverTool
hover = HoverTool()
hover.tooltips = [
    ("Category", "@categories"),
    ("Count", "@counts"),
]
p.add_tools(hover)

# Save plot to HTML
output_file("course_availability.html")

# Save the plot
save(p)

# Dropdown widgets for year and semester
semester_select = Select(title="Semester", value="Spring", options=["Spring", "Summer", "Winter"])
year_select = Select(title="Year", value="2024", options=[str(x) for x in range(2021, 2025)])

# Update function when dropdowns change
def update_plot(attr, old, new):
    selected_year = int(year_select.value)
    selected_semester = semester_select.value
    active_count, inactive_count, ratio = create_course_availability_and_activity_for_semester(courses_df, selected_year, selected_semester)
    source.data = dict(categories=['Active', 'Inactive'], counts=[active_count, inactive_count])

# Add callback for dropdowns
semester_select.on_change('value', update_plot)
year_select.on_change('value', update_plot)

# Layout
layout = column(row(year_select, semester_select), p)

# Add to current document
curdoc().add_root(layout)
curdoc().title = "Course Availability"
