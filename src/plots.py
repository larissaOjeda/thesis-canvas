from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.plotting import figure
import pandas as pd


def create_average_score_plot(average_scores_df):
    """
    Creates a Bokeh plot for average assignment score per course.
    """
    source = ColumnDataSource(average_scores_df)
    
    plot = figure(
      x_range=average_scores_df['course_id'],
      title="Average Assignment Score per Course",
      x_axis_label="Course ID",
      y_axis_label="Average Score",
      width=700,
      height=400
    )
    
    
    plot.vbar(
        x='course_id',
        top='value.score',
        width=0.9,
        source=source,
        fill_color='navy',
        line_color='white'
    )
    
    # Add hover tool
    hover = HoverTool(tooltips=[
        ("Course ID", "@course_id"),
        ("Average Score", "@{value.score}{0.2f}")
    ])
    plot.add_tools(hover)
    
    # Rotate x-axis labels if there are many courses
    plot.xaxis.major_label_orientation = 1.0  # Radians (~57 degrees)
    
    return plot
