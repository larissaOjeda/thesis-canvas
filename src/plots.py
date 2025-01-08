from bokeh.plotting import figure
from bokeh.models import (
    ColumnDataSource, 
    HoverTool, 
    BoxAnnotation,
    Span,
    Label,
)
from bokeh.transform import factor_cmap, dodge
from bokeh.palettes import Blues8

import math
import pandas as pd
import numpy as np 


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
        width=600,
        height=400,
        title=f"Course Requirements Progress Analysis",
        toolbar_location="above",
        tools="pan,box_zoom,reset,save",
        y_range=(y_min, y_max)
    )

    # Add background shading for different ranges
    low_box = BoxAnnotation(top=60, fill_color='red', fill_alpha=0.5)
    mid_box = BoxAnnotation(bottom=60, top=80, fill_color='yellow', fill_alpha=0.5)
    high_box = BoxAnnotation(bottom=80, fill_color='green', fill_alpha=0.5)
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
    colors = {"Top": "#00A878", "Bottom": "#D62246", "Average": "#4B8BBE"}
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
    colors = ["#d36e70", "#51d1f6", "#369280"]

    # Create scatter plot
    p = figure(
        width=700,
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
            ("Course name", "@course_name"),
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



def create_course_completion_rate(source, N=10, avg_count=15):
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
        width=600,
        height=400,
        title=f"Course Completion Rates Analysis (Top {N}, Bottom{N} and Average {N})",
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

    low_box = BoxAnnotation(top=low_range, fill_color='#FFB2B2', fill_alpha=0.3)  # Light red
    mid_box = BoxAnnotation(bottom=low_range, top=mid_range_upper, fill_color='#51d1f6', fill_alpha=0.15)  # Light blue
    high_box = BoxAnnotation(bottom=mid_range_upper, top=100, fill_color='#09a416', fill_alpha=0.15)  # Light green
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


    colors = {"Top": "#00A878", "Bottom": "#D62246", "Average": "#4B8BBE"}
    for category, color in colors.items():
        category_source = ColumnDataSource(selected_df[selected_df["category"] == category])
        p.line(x="course_id_str", y="completion_rate", color=color, legend_label=category, source=category_source, line_width=2)
        p.scatter(x="course_id_str", y="completion_rate", size=6, color=color, legend_label=category, source=category_source)

    p.legend.title = "Category"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.legend.background_fill_alpha = 0.6

    p.xaxis.major_label_orientation = 0.8

    return p


def plot_learning_objective_completion(source):
    # Convert ColumnDataSource to DataFrame
    df = source.to_df()
    df['course_id'] = df['course_id'].astype(str)

    # Calculate averages
    avg_achievement_avg = df['avg_achievement_percentage'].mean()
    mastery_percentage_avg = df['mastery_percentage'].mean()

    # Recreate ColumnDataSource with updated DataFrame
    source = ColumnDataSource(df)
    course_ids = df['course_id'].tolist()

    # Define hover tool
    hover = HoverTool(
        tooltips=[
            ('Course ID', '@course_id'),
            ('Course name', '@course_name'),
            ('Achievement', '@avg_achievement_percentage{0.0}%'),
            ('Mastery', '@mastery_percentage{0.0}%'),
        ]
    )

    # Create figure with tools
    p = figure(
        x_range=course_ids,
        width=600,
        height=400,
        title="Learning Objective Completion by Course",
        toolbar_location='above',
        tools=[hover, 'pan', 'box_zoom', 'wheel_zoom', 'save', 'reset']
    )

    # Plot avg_achievement_percentage
    bar1 = p.vbar(
        x=dodge('course_id', -0.2, range=p.x_range), 
        top='avg_achievement_percentage', 
        width=0.25, 
        source=source,
        color="#497e76",
        legend_label=f"Achievement Percentage (Avg: {avg_achievement_avg:.1f}%)"
    )

    # Plot mastery_percentage
    bar2 = p.vbar(
        x=dodge('course_id', 0.2, range=p.x_range), 
        top='mastery_percentage', 
        width=0.25, 
        source=source,
        color="#ecb653",
        legend_label=f"Mastery Percentage (Avg: {mastery_percentage_avg:.1f}%)"
    )

    # Add average dotted lines
    p.line(
        x=p.x_range.factors, 
        y=[avg_achievement_avg] * len(p.x_range.factors),
        line_width=2, 
        line_dash="dotted", 
        color="blue"
    )

    p.line(
        x=p.x_range.factors, 
        y=[mastery_percentage_avg] * len(p.x_range.factors),
        line_width=2, 
        line_dash="dotted", 
        color="green"
    )

    # Customize appearance
    p.x_range.range_padding = 0.1
    p.y_range.start = 0
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = 'Percentage'
    p.xaxis.axis_label = 'Course ID'
    p.xaxis.major_label_orientation = 1.2

    # Configure legend
    p.legend.location = "center_right"
    p.legend.click_policy = "hide"

    return p


def create_students_retention_rate_plot(source, percentile=75):
    """
    Creates a retention rate plot filtered by specified percentile
    Args:
        source: ColumnDataSource with the data
        percentile: The percentile threshold for filtering (e.g., 75 for top 25%)
    """
    # Convert source to DataFrame for filtering
    df = pd.DataFrame(source.data)
    
    # Apply filters
    df = df[~((df['total_enrollments'] > 8) & (df['active_enrollments'] == 1))]
    df = df[df['total_enrollments'] >= 5]
    
    # Filter by specified percentile
    threshold = np.percentile(df['retention_rate_percentage'], percentile)
    df = df[df['retention_rate_percentage'] >= threshold]
    
    # Convert course_id to string for x-axis
    df['course_id_str'] = df['course_id'].astype(str)
    
    # Create new source with filtered data
    filtered_source = ColumnDataSource(df)
    
    # Create figure
    p = figure(
        x_range=df['course_id_str'].tolist(),
        width=750,
        height=400,
        title=f"Course Retention Rates (Top {100-percentile}%)",
        toolbar_location="right",
        x_axis_label="Course ID",
        y_axis_label="Retention Rate (%)"
    )
    
    # Create bars
    bars = p.vbar(
        x='course_id_str',
        top='retention_rate_percentage',
        width=0.7,
        source=filtered_source,
        fill_color=Blues8[3],
        line_color=None
    )
    
    # Add hover tool for bars
    hover = HoverTool(
        tooltips=[
            ('Course', '@course_name'),
            ('Course ID', '@course_id_str'),
            ('Retention Rate', '@retention_rate_percentage{0.0}%'),
            ('Total Enrollments', '@total_enrollments'),
            ('Active Enrollments', '@active_enrollments'),
            ('Term', '@term_name')
        ],
        renderers=[bars]
    )
    p.add_tools(hover)
    
    # Style the plot
    p.y_range.start = 0
    p.y_range.end = max(df['retention_rate_percentage']) * 1.1
    p.xgrid.grid_line_color = None
    p.xaxis.major_label_orientation = math.pi/4
    p.xaxis.axis_label_text_font_size = '10pt'
    p.xaxis.major_label_text_font_size='8pt'
    
    # Compute statistics
    avg_retention = df['retention_rate_percentage'].mean()
    median_retention = df['retention_rate_percentage'].median()
    
    # Add statistics to the title
    p.title.text = (
        f"Course Retention Rates (Top {100-percentile}%)\n"
    )

    # Create data sources for avg and median lines
    line_source = ColumnDataSource(data={
        'x': p.x_range.factors, 
        'avg_y': [avg_retention] * len(p.x_range.factors),
        'median_y': [median_retention] * len(p.x_range.factors),
        'avg_value': [avg_retention] * len(p.x_range.factors),
        'median_value': [median_retention] * len(p.x_range.factors)
    })
    
    # Add lines
    avg_line = p.line(
        x='x', y='avg_y', source=line_source,
        line_color='gray', line_dash='dashed', line_width=2
    )
    median_line = p.line(
        x='x', y='median_y', source=line_source,
        line_color='black', line_dash='dotted', line_width=2
    )
    
    # Add hover tool for both lines
    line_hover = HoverTool(
        renderers=[avg_line, median_line],
        tooltips=[
            ("Avg Retention Rate", "@avg_value{0.1f}%"),
            ("Median Retention Rate", "@median_value{0.1f}%")
        ]
    )
    p.add_tools(line_hover)

    # Add labels for average and median lines
    label_avg = Label(
        x=730,                # Positioned near the right side (pixels from the left)
        y=avg_retention,      
        x_units='screen',
        y_units='data',
        text=f"Avg: {avg_retention:.1f}%", 
        text_font_size='8pt', 
        text_color='gray'
    )
    label_median = Label(
        x=730,                # Positioned near the right side
        y=median_retention,
        x_units='screen',
        y_units='data',
        text=f"Median: {median_retention:.1f}%", 
        text_font_size='8pt', 
        text_color='black'
    )
    p.add_layout(label_avg)
    p.add_layout(label_median)
    
    return p
