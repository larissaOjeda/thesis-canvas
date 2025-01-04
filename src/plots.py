from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, 
    HoverTool, 
    BoxAnnotation,
    Span,
    Label,
)
from bokeh.transform import factor_cmap, dodge
from bokeh.palettes import Spectral6

import pandas as pd


def create_progress_in_course_requirements(source, N=10, avg_count=10):
    """
    Creates a line plot showing progress in course requirements for:
    - Top N courses
    - Bottom N courses
    - Average N courses closest to the overall average completion percentage.
    """
    # Data preparation
    df = source.to_df()
    df = df[df["completion_percentage"] < 100]

    sorted_df = df.sort_values(by="completion_percentage", ascending=False)
    top_n = sorted_df.head(N)
    bottom_n = sorted_df.tail(N)

    avg_completion = df["completion_percentage"].mean()
    df["avg_diff"] = abs(df["completion_percentage"] - avg_completion)
    avg_courses = df.nsmallest(avg_count, "avg_diff")

    selected_df = pd.concat([top_n, bottom_n, avg_courses])
    selected_df["course_id_str"] = selected_df["course_id"].astype(str)
    
    # Calculate y-axis range with padding
    max_rate = selected_df['completion_percentage'].max()
    min_rate = selected_df['completion_percentage'].min()
    y_padding = 5
    y_max = min(max_rate + y_padding, 100)
    y_min = max(min_rate - y_padding, 0)

    # Assign categories
    selected_df["category"] = (
        ["Top"] * len(top_n) +
        ["Bottom"] * len(bottom_n) +
        ["Average"] * len(avg_courses)
    )

    # Create figure
    p = figure(
        x_range=selected_df["course_id_str"],
        width=800,
        height=400,
        title=f"Course Requirements Progress Analysis",
        toolbar_location="above",
        tools="pan,box_zoom,reset,save",
        y_range=(y_min, y_max)
    )

    # Add background shading for different ranges
    low_box = BoxAnnotation(top=60, fill_color='red', fill_alpha=0.1)
    mid_box = BoxAnnotation(bottom=60, top=80, fill_color='yellow', fill_alpha=0.1)
    high_box = BoxAnnotation(bottom=80, fill_color='green', fill_alpha=0.1)
    p.add_layout(low_box)
    p.add_layout(mid_box)
    p.add_layout(high_box)

    # Add reference line for average
    avg_line = Span(
        location=avg_completion,
        dimension='width',
        line_color='gray',
        line_dash='dashed',
        line_width=1
    )
    p.add_layout(avg_line)

    # Plot lines and points for each category
    colors = {"Top": "#2ecc71", "Bottom": "#e74c3c", "Average": "#3498db"}
    line_styles = {
        "Top": {"line_dash": "solid", "line_width": 2},
        "Bottom": {"line_dash": "dashed", "line_width": 2},
        "Average": {"line_dash": "dotted", "line_width": 2}
    }

    # Add hover tool
    hover = HoverTool(
        tooltips=[
            ('Course ID', '@course_id'),
            ('Completion %', '@completion_percentage{0.2f}%'),
            ('Category', '@category')
        ],
        mode='mouse',
        point_policy='snap_to_data'
    )
    p.add_tools(hover)

    for category, color in colors.items():
        category_source = ColumnDataSource(
            selected_df[selected_df["category"] == category]
        )
        
        # Add line
        p.line(
            x="course_id_str",
            y="completion_percentage",
            color=color,
            legend_label=category,
            source=category_source,
            **line_styles[category]
        )
        
        # Add points
        p.scatter(
            x="course_id_str",
            y="completion_percentage",
            size=4,
            color=color,
            legend_label=category,
            source=category_source,
            muted_alpha=0.2
        )

    # Styling
    p.yaxis.axis_label = "Completion Percentage (%)"
    p.xaxis.axis_label = "Course ID"
    p.xgrid.grid_line_color = None
    p.grid.grid_line_color = "gray"
    p.grid.grid_line_alpha = 0.1
    p.xaxis.major_label_orientation = 0.8
    
    # Legend styling
    p.legend.title = "Category"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.legend.background_fill_alpha = 0.7

    # Background styling
    p.background_fill_color = "#f9f9f9"
    p.border_fill_color = "#ffffff"
    p.outline_line_color = None

    return p


def create_feedback_scatter(source, N=25, avg_count=25):
    """
    Creates a scatter plot for average feedback time with:
    - Top N courses
    - Bottom N courses
    - Avg N courses closest to the overall average feedback time.
    """
    df = source.to_df()

    # Sort by feedback time
    sorted_df = df.sort_values(by="avg_feedback_days", ascending=False)

    # Select top N and bottom N courses
    top_n = sorted_df.head(N)
    bottom_n = sorted_df.tail(N)

    # Calculate the average feedback time
    avg_feedback = df["avg_feedback_days"].mean()

    # Find the avg_count courses closest to the average feedback time
    df["avg_diff"] = abs(df["avg_feedback_days"] - avg_feedback)
    avg_courses = df.nsmallest(avg_count, "avg_diff")

    # Combine top, bottom, and average courses
    selected_df = pd.concat([top_n, bottom_n, avg_courses])

    # Assign categories for color distinction
    selected_df["category"] = (
        ["Top"] * len(top_n) +
        ["Bottom"] * len(bottom_n) +
        ["Average"] * len(avg_courses)
    )

    # Normalize feedback time for bubble size
    min_size, max_size = 5, 20  # Bubble size range
    selected_df["bubble_size"] = (
        ((selected_df["avg_feedback_days"] - selected_df["avg_feedback_days"].min()) /
         (selected_df["avg_feedback_days"].max() - selected_df["avg_feedback_days"].min())) *
        (max_size - min_size) + min_size
    )

    # Prepare the data source
    source = ColumnDataSource(selected_df)

    # Custom color palette: Red (Top), Blue (Bottom), Green (Average)
    colors = ["red", "blue", "green"]

    # Create scatter plot
    p = figure(
        width=800,
        height=400,
        title=f"Top {N}, Bottom {N}, and Avg {avg_count} Courses by Feedback Time",
        x_axis_label="Course ID",
        y_axis_label="Feedback Time (hours)",
        toolbar_location="above",
        tools="pan,box_zoom,reset,save",
    )

    # Add scatter points with dynamic size
    scatter = p.scatter(
        x="course_id",
        y="avg_feedback_days",
        size="bubble_size",  # Bubble size based on feedback time
        color=factor_cmap("category", palette=colors, factors=["Top", "Bottom", "Average"]),
        legend_field="category",
        source=source,
    )

    # Add hover tool
    hover = HoverTool(
        renderers=[scatter],
        tooltips=[
            ("Course ID", "@course_id"),
            ("Feedback Time (days)", "@avg_feedback_days{0.0} days"),
            ("Category", "@category"),
        ],
    )
    p.add_tools(hover)

    # Add horizontal line for the average feedback time
    p.line(
        x=[selected_df["course_id"].min(), selected_df["course_id"].max()],
        y=[avg_feedback, avg_feedback],
        line_dash="dotted",
        line_width=2,
        color="black",
        legend_label=f"Average: {avg_feedback:.2f} hours",
    )

    # Style the plot
    p.add_layout(p.legend[0], "right")
    p.background_fill_color = "#f9f9f9"
    p.border_fill_color = "#ffffff"
    p.outline_line_color = None  # Remove plot borders
    p.legend.location = "top_left"
    p.legend.label_text_font_size = "10pt"

    return p


def create_course_completion_rate(source):
    """
    Creates a green bar chart showing course completion rates.
    Filters the DataFrame so that only certain course IDs
    (e.g., multiples of 1000) are displayed.
    """
    df = source.to_df()

    # 2) Convert course_id to string for factor-based x-axis
    df['course_id_str'] = df['course_id'].astype(str)

    # 3) Create a ColumnDataSource
    source = ColumnDataSource(df)

    # 4) Create figure
    p = figure(
        x_range=df['course_id_str'],
        width=800,
        height=400,
        title='Course Completion Rate (Filtered by ID)',
        toolbar_location='above',
        tools='pan,box_zoom,reset,save'
    )

    # 5) Add green bars
    p.vbar(
        x='course_id_str',
        top='completion_rate',
        width=0.7,
        color='green',
        source=source
    )

    # 6) Add a hover tooltip (the “label cursor”)
    hover = HoverTool(
        tooltips=[
            ('Course ID', '@course_id'),
            ('Completion Rate', '@completion_rate%')
        ]
    )
    p.add_tools(hover)

    # 7) Customize axes
    p.xaxis.major_label_orientation = 0.8  # tilt labels if needed
    p.xaxis.axis_label = 'Course ID'
    p.yaxis.axis_label = 'Completion Rate (%)'
    p.y_range.start = 0
    p.y_range.end = 100  # if you know rates can’t exceed 100

    return p

def create_course_completion_rate(source, N=10, avg_count=10):
    """
    Creates a line plot showing completion rates with zone annotations and labels.
    """
    df_source = source.to_df() if hasattr(source, 'to_df') else source

    df = df_source[
        (df_source['completion_rate'] > 0) &
        (df_source['completion_rate'] < 100) &
        (df_source['total_enrolled'] > 0)
    ].copy()

    if "completion_rate" not in df.columns:
        raise ValueError("The source must contain a 'completion_rate' column.")

    sorted_df = df.sort_values(by="completion_rate", ascending=False)
    top_n = sorted_df.head(N)
    bottom_n = sorted_df.tail(N)

    avg_completion = df["completion_rate"].mean()
    std_dev_completion = df["completion_rate"].std()

    low_range = max(0, avg_completion - std_dev_completion)
    mid_range_upper = min(100, avg_completion + std_dev_completion)

    df["avg_diff"] = abs(df["completion_rate"] - avg_completion)
    avg_courses = df.nsmallest(avg_count, "avg_diff")

    selected_df = pd.concat([top_n, bottom_n, avg_courses])
    selected_df["category"] = (["Top"] * len(top_n) + ["Bottom"] * len(bottom_n) + ["Average"] * len(avg_courses))
    selected_df["course_id_str"] = selected_df["course_id"].astype(str)

    p = figure(
        width=700,
        height=400,
        title="Course Completion Rates Analysis",
        x_axis_label="Course ID",
        y_axis_label="Completion Rate (%)",
        toolbar_location="above",
        tools="pan,box_zoom,reset,save,hover",
        x_range=selected_df["course_id_str"],
        y_range=(0, 100)
    )

    hover = HoverTool(tooltips=[
        ('Course ID', '@course_id_str'),
        ('Completion Rate', '@completion_rate{0.0}%'),
        ('Total Enrolled', '@total_enrolled'),
        ('Completed Count', '@completed_count'),
        ('Category', '@category')
    ])
    p.add_tools(hover)

    p.grid.grid_line_color = "gray"
    p.grid.grid_line_alpha = 0.1
    p.xgrid.grid_line_color = None

    low_box = BoxAnnotation(top=low_range, fill_color='red', fill_alpha=0.1)
    mid_box = BoxAnnotation(bottom=low_range, top=mid_range_upper, fill_color='yellow', fill_alpha=0.1)
    high_box = BoxAnnotation(bottom=mid_range_upper, top=100, fill_color='green', fill_alpha=0.1)
    p.add_layout(low_box)
    p.add_layout(mid_box)
    p.add_layout(high_box)

    label_y_offset = 5

    low_label = Label(
        x=10, y=low_range - label_y_offset,
        text="Bottom Area",
        text_color="gray",
        text_font_size="10pt",
        text_align="left",
        y_units='data'
    )
    mid_label = Label(
        x=10, y=avg_completion + 20,
        text="Average Area",
        text_color="gray",
        text_font_size="10pt",
        text_align="left",
        y_units='data'
    )
    high_label = Label(
        x=10, y=mid_range_upper + label_y_offset,
        text="Top Area",
        text_color="gray",
        text_font_size="10pt",
        text_align="left",
        y_units='data'
    )
    p.add_layout(low_label)
    p.add_layout(mid_label)
    p.add_layout(high_label)

    # Add the average dashed line
    avg_line = Span(
        location=avg_completion,
        dimension='width',
        line_color='gray',
        line_dash='dotted',  # Make it dashed
        line_width=1
    )
    p.add_layout(avg_line)

    avg_label = Label(
        x=len(selected_df["course_id_str"]) // 1.6,
        y=avg_completion + 2,  # Position slightly above the line
        text=f"Avg: {avg_completion:.2f}%",
        text_color="gray",
        text_font_size="10pt",
        text_align="center"
    )
    p.add_layout(avg_label)


    colors = {"Top": "green", "Bottom": "red", "Average": "blue"}
    for category, color in colors.items():
        category_source = ColumnDataSource(selected_df[selected_df["category"] == category])
        p.line(x="course_id_str", y="completion_rate", color=color, legend_label=category, source=category_source, line_width=2)
        p.scatter(x="course_id_str", y="completion_rate", size=6, color=color, legend_label=category, source=category_source)

    p.legend.title = "Category"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.legend.background_fill_alpha = 0.7

    p.xaxis.major_label_orientation = 0.8

    return p

from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, HoverTool
from bokeh.palettes import Spectral6
from bokeh.transform import dodge

def plot_learning_objective_completion(source):
    # Convert ColumnDataSource to DataFrame
    df = source.to_df()
    df['course_id'] = df['course_id'].astype(str)

    # Recreate ColumnDataSource with updated DataFrame
    source = ColumnDataSource(df)
    course_ids = df['course_id'].tolist()

    # Create figure with updated size
    p = figure(
        x_range=course_ids,
        width=600,  # Increased width
        height=400,  # Reduced height
        title="Learning Objective Completion by Course",
        toolbar_location=None,
        tools=""
    )

    # Plot avg_achievement_percentage
    p.vbar(
        x=dodge('course_id', -0.17, range=p.x_range), 
        top='avg_achievement_percentage', 
        width=0.30, 
        source=source,
        legend_label="Average Achievement Percentage", 
        color=Spectral6[0]
    )

    # Plot mastery_percentage
    p.vbar(
        x=dodge('course_id', 0.17, range=p.x_range), 
        top='mastery_percentage', 
        width=0.30, 
        source=source,
        legend_label="Mastery Percentage", 
        color=Spectral6[1],
        alpha=0.8
    )

    # Customize appearance
    p.x_range.range_padding = 0.1
    p.y_range.start = 0
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = 'Percentage'
    p.xaxis.axis_label = 'Course ID'
    p.xaxis.major_label_orientation = 1.2
    p.legend.location = "top_left"
    p.legend.orientation = "horizontal"

    # Add hover tool
    hover = HoverTool()
    hover.tooltips = [
        ("Course ID", "@course_id"),
        ("Average Achievement Percentage", "@avg_achievement_percentage%"),
        ("Mastery Percentage", "@mastery_percentage%")
    ]
    p.add_tools(hover)

    return p


