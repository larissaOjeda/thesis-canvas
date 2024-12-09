

from bokeh.plotting import figure, show
from bokeh.models import HoverTool
year = 2023
semester = "Spring"

active_count, inactive_count, ratio = create_ratio_of_course_availability_and_activity_for_semester(courses_df, year, semester)




def plot_active_inactive_courses(data):
    p = figure(title="Active vs. Inactive Courses", x_axis_label="Month", y_axis_label="Number of Courses")

    # Plot the active courses
    p.line(x='month', y='active_count', source=data, line_color="blue", legend_label="Active")

    # Plot the inactive courses
    p.line(x='month', y='inactive_count', source=data, line_color="orange", legend_label="Inactive")

    # Add tooltips for more information
    hover = HoverTool(tooltips=[("Month", "@month"), ("Active", "@active_count"), ("Inactive", "@inactive_count")])
    p.add_tools(hover)

    p.legend.location = "top_left"
    show(p)





