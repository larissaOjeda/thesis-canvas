
from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, Select, HoverTool, Label, LinearColorMapper, Select, ColorBar
from bokeh.plotting import figure
from bokeh.transform import cumsum
from bokeh.plotting import figure
from bokeh.transform import linear_cmap
from bokeh.palettes import Viridis256
import pandas as pd
import numpy as np
from math import pi

from kpi_calculator import (
    create_ratio_of_course_availability_and_activity_for_semester,
    create_student_retention_rate,
    calculate_tasks_completion_rate,
    calculate_average_score,
    calculate_score_distribution, 
    calculate_feedback_time_vs_assignment_count,
)
from utils import constants


courses_df = pd.read_csv(constants.COURSES_PATH)
enrollments_df = pd.read_csv(constants.ENROLLMENTS_PATH)
assignments_df = pd.read_csv(constants.ASSIGNMENTS_PATH)
submissions_df =  pd.read_csv(constants.SUBMISSIONS_PATH)
scores_df = pd.read_csv(constants.SCORES_PATH)

# Initial plot data for Spring 2024
year = 2024
semester = 'Spring'
AVG_LINE_COLOR = "#FFA07A"

active_count, inactive_count, ratio = create_ratio_of_course_availability_and_activity_for_semester(courses_df, year, semester)
retention_rate = create_student_retention_rate(enrollments_df, year, semester)
completion_rate = calculate_tasks_completion_rate(assignments_df, submissions_df, year, semester)
avg_score = calculate_average_score(scores_df, year, semester)

# Calculate initial score distribution for the histogram
scores = calculate_score_distribution(scores_df, year, semester)
hist, edges = np.histogram(scores, bins=20, range=[0, 100])

# Data sources for the plots
course_source = ColumnDataSource(data=dict(categories=['Active', 'Inactive'], counts=[active_count, inactive_count]))

retention_source = ColumnDataSource(data=dict(start=[0], end=[retention_rate / 100 * 2 * 3.14159], retention=[retention_rate]))
retention_text_source = ColumnDataSource(data=dict(rate_text=[f"{retention_rate:.1f}%"]))

completion_source = ColumnDataSource(data=dict(start=[0], end=[completion_rate / 100 * 2 * 3.14159], completion=[completion_rate]))
completion_text_source = ColumnDataSource(data=dict(rate_text=[f"{completion_rate:.1f}%"]))

avg_score_source = ColumnDataSource(data=dict(start=[0], end=[avg_score / 100 * 2 * 3.14159], avg_score=[avg_score]))
avg_score_text_source = ColumnDataSource(data=dict(rate_text=[f"{avg_score:.1f}%"]))

hist_source = ColumnDataSource(data=dict(top=hist, left=edges[:-1], right=edges[1:]))


# Create Course Availability plot
course_plot = figure(x_range=['Active', 'Inactive'], y_axis_label="Number of courses", height=350, width=700, title="Course Availability", toolbar_location=None)
course_plot.vbar(x='categories', top='counts', width=0.9, source=course_source)

# Student Retention Rate plot
retention_plot = figure(width=350, height=350, title="Student Retention Rate", toolbar_location=None, x_range=(-1, 1), y_range=(-1, 1))
retention_plot.annular_wedge(x=0, y=0, inner_radius=0.4, outer_radius=0.9, start_angle='start', end_angle='end', source=retention_source, color="blue")
retention_plot.text(x=0, y=0, text='rate_text', text_align="center", text_baseline="middle", text_font_size="20pt", source=retention_text_source)

# Create Completion Rate plot using Annular Wedge
completion_plot = figure(width=350, height=350, title="Assignment Completion Rate", toolbar_location=None, x_range=(-1, 1), y_range=(-1, 1))
completion_plot.annular_wedge(x=0, y=0, inner_radius=0.4, outer_radius=0.9, start_angle='start', end_angle='end', source=completion_source, color="green")
completion_plot.text(x=0, y=0, text='rate_text', text_align="center", text_baseline="middle", text_font_size="20pt", source=completion_text_source)

# Create Score Distribution Histogram
histogram_plot = figure(height=500, width=700, x_axis_label="Score (%)", y_axis_label="Count", title="Score Distribution Histogram")
histogram_plot.quad(top='top', bottom=0, left='left', right='right', source=hist_source, fill_color="navy", line_color="white", alpha=0.7)
histogram_plot.line(
    x=[avg_score, avg_score], y=[0, max(hist)],
    line_width=2, color=AVG_LINE_COLOR, legend_label="Average Score", line_dash="dashed"
)

# Optional: Add label to the line
avg_score_label = Label(x=avg_score, y=max(hist), text=f"Avg Score: {avg_score:.1f}",
                        text_align="center", text_baseline="bottom", text_color=AVG_LINE_COLOR)
histogram_plot.add_layout(avg_score_label)

# Function to calculate feedback data for scatter plot
def get_feedback_data(year, semester):
    data = calculate_feedback_time_vs_assignment_count(submissions_df, year=year, semester=semester)
    data['average_feedback_time'] = data['average_feedback_time'].clip(upper=1000)
    data['size'] = (data['assignment_count'] / data['assignment_count'].max() * 40).clip(lower=5)
    data['course_id'] = data['value.course_id'].astype(str)
    return data

# Initialize scatter plot data
feedback_data = get_feedback_data(year, semester)
feedback_time_source = ColumnDataSource(feedback_data)

# Create scatter plot
color_mapper = LinearColorMapper(palette=Viridis256, low=feedback_data['average_feedback_time'].min(), high=feedback_data['average_feedback_time'].max())
feedback_time_plot = figure(width=900, height=500, title="Average Feedback Time vs. Number of Assignments",
                            x_axis_label="Number of Assignments", y_axis_label="Average Feedback Time (Hours)",
                            toolbar_location="above", tools="pan,wheel_zoom,box_zoom,reset")

feedback_time_plot.scatter(x='assignment_count', y='average_feedback_time', size='size', source=feedback_time_source,  # Use scatter instead of circle
                          fill_color=linear_cmap('average_feedback_time', Viridis256,
                                                 min(feedback_data['average_feedback_time']),
                                                 max(feedback_data['average_feedback_time'])),
                          line_color=None, alpha=0.7)
feedback_time_plot.add_tools(HoverTool(tooltips=[("Course ID", "@course_id"), ("Average Feedback Time (hrs)", "@average_feedback_time{0.0}"),
                                                 ("Number of Assignments", "@assignment_count")]))
feedback_time_plot.add_layout(ColorBar(color_mapper=color_mapper, label_standoff=12, width=8, location=(0, 0)), 'right')

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

# Add hover for Score Distribution Histogram
hover_histogram = HoverTool(tooltips=[("Count", "@top")])
histogram_plot.add_tools(hover_histogram)


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
    retention_source.data = dict(start=[0], end=[retention_rate / 100 * 2 * 3.14159], retention=[retention_rate])
    retention_text_source.data = dict(rate_text=[f"{retention_rate:.1f}%"])

    # Update assignment completion rate data
    completion_rate = calculate_tasks_completion_rate(assignments_df, submissions_df, selected_year, selected_semester)
    completion_source.data = dict(start=[0], end=[completion_rate / 100 * 2 * 3.14159], completion=[completion_rate])
    completion_text_source.data = dict(rate_text=[f"{completion_rate:.1f}%"])

    # Update feedback time
    feedback_time = get_feedback_data(selected_year, selected_semester)
    feedback_time_source.data = ColumnDataSource.from_df(feedback_time)

    # Update score distribution histogram
    scores = calculate_score_distribution(scores_df, selected_year, selected_semester)
    hist, edges = np.histogram(scores, bins=20, range=[0, 100])
    hist_source.data = dict(top=hist, left=edges[:-1], right=edges[1:])

# Add callback for dropdowns
semester_select.on_change('value', update_plots)
year_select.on_change('value', update_plots)

# Layout for the dashboard with plot labels
dashboard_layout = column(
    row(year_select, semester_select, sizing_mode='stretch_width'),
    row(course_plot, retention_plot, completion_plot, sizing_mode='stretch_width'),
    row(histogram_plot, feedback_time_plot, sizing_mode='stretch_width')  # Add the histogram to the layout
)

# Add the layout to the current document
curdoc().add_root(dashboard_layout)
curdoc().title = "Course Availability, Retention, Completion, and Score Distribution Dashboard"