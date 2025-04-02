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

ITAM_COLOR = "#019B7A"
LIGHTER_ITAM_COLOR = "#9FE1CC"
DARKER_ITAM_COLOR = "#014D3E"

COLOR_FOR_WORST = "#FF6F61"
COLOR_FOR_AVERAGE = "#8FAADC"
COLOR_FOR_BEST = "#4CAF50"

TEXT_FONT_SIZE = "12pt"
HEIGHT = 500 

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
        height=HEIGHT,
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
    p.title.text_font_size = TEXT_FONT_SIZE

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

## TO DELETE
# def create_feedback_bar_chart(source, N=10, avg_count=10):
#     """
#     Creates a sorted horizontal bar chart for average feedback time.
#     N: Number of top and bottom courses to display
#     avg_count: Number of average courses closest to the overall average feedback time
#     """
#     df = source.to_df()

#     # Sort by feedback time (descending)
#     sorted_df = df.sort_values(by="avg_feedback_days", ascending=False)

#     # Calculate the average feedback time
#     avg_feedback = df["avg_feedback_days"].mean()

#     # Select top N, bottom N, and average N courses
#     top_n = sorted_df.head(N)
#     bottom_n = sorted_df.tail(N)

#     # Find the avg_count courses closest to the overall average feedback time
#     sorted_df['avg_diff'] = abs(sorted_df['avg_feedback_days'] - avg_feedback)
#     avg_courses = sorted_df.nsmallest(avg_count, 'avg_diff')

#     # Combine top, bottom, and average courses
#     selected_df = pd.concat([top_n, bottom_n, avg_courses])

#     # Assign categories for color distinction
#     selected_df['category'] = (
#         ['Peores'] * len(top_n) +
#         ['Mejores'] * len(bottom_n) +
#         ['Promedio'] * len(avg_courses)
#     )

#     # Convert course_id to string for x-axis
#     selected_df['course_id_str'] = selected_df['course_id'].astype(str)

#     # Prepare the data source
#     source = ColumnDataSource(selected_df)

#     # Color map for categories
#     color_map = factor_cmap('category', palette=['#D62246', '#4B8BBE', '#00A878'], factors=['Peores', 'Mejores', 'Mejores'])

#     # Create the figure
#     p = figure(
#         y_range=selected_df['course_id_str'][::-1],  # Reverse for descending order
#         width=800,
#         height=HEIGHT,
#         title="Tiempo promedio de retroalimentación (Mejores, promedios y peores 10)",
#         toolbar_location='above',
#         x_axis_label="Average Feedback Time (days)",
#         tools="pan,box_zoom,reset,save",
#         margin=(20, 20, 20, 20),
#     )

#     # Add horizontal bars
#     p.hbar(
#         y='course_id_str', 
#         right='avg_feedback_days', 
#         height=0.4,
#         color=color_map,
#         source=source,
#         legend_field='category'
#     )

#     # Add hover tool
#     hover = HoverTool(
#         tooltips=[
#             ("Course ID", "@course_id"),
#             ("Course name", "@course_name"),
#             ("Avg Feedback Time (days)", "@avg_feedback_days{0.00}"),
#             ("Category", "@category"),
#         ]
#     )
#     p.add_tools(hover)

#     # Add a vertical reference line for the average feedback time
#     avg_line = Span(
#         location=avg_feedback,
#         dimension='height',
#         line_color='black',
#         line_dash='dotted',
#         line_width=2
#     )
#     p.add_layout(avg_line)

#     # Add a label for the average line
#     avg_label = Label(
#         x=avg_feedback + 1,
#         y=len(selected_df['course_name']) - 1,
#         text=f"Avg: {avg_feedback:.2f} days",
#         text_font_size="10pt",
#         text_color="black"
#     )
#     p.add_layout(avg_label)

#     # Customize the legend
#     p.legend.title = "Tiempo de retroalimentación"
#     p.legend.location = "top_right"
#     p.legend.orientation = "vertical"
#     p.legend.click_policy = "hide"

#     # Style the plot
#     p.background_fill_color = "#f9f9f9"
#     p.border_fill_color = "#ffffff"
#     p.outline_line_color = None
#     p.title.text_font_size = TEXT_FONT_SIZE

#     return p

def create_feedback_bar_chart(source, N=10, avg_count=10):
    """
    Creates a sorted horizontal bar chart for average feedback time.
    N: Number of top and bottom courses to display
    avg_count: Number of average courses closest to the overall average feedback time
    """
    df = source.to_df()

    # Sort by feedback time (descending)
    sorted_df = df.sort_values(by="avg_feedback_days", ascending=False)

    # Calculate the average feedback time
    avg_feedback = df["avg_feedback_days"].mean()

    # Select top N, bottom N, and average N courses
    top_n = sorted_df.head(N)
    bottom_n = sorted_df.tail(N)

    # Find the avg_count courses closest to the overall average feedback time
    sorted_df['avg_diff'] = abs(sorted_df['avg_feedback_days'] - avg_feedback)
    avg_courses = sorted_df.nsmallest(avg_count, 'avg_diff')

    # Combine top, bottom, and average courses
    selected_df = pd.concat([top_n, bottom_n, avg_courses])

    # Assign categories for color distinction
    selected_df['category'] = (
    ['Peores'] * len(top_n) +
    ['Mejores'] * len(bottom_n) +
    ['Promedio'] * len(avg_courses)
)

    # Convert course_id to string for x-axis
    selected_df['course_id_str'] = selected_df['course_id'].astype(str)
    selected_df['course_label'] = selected_df['course_name'] + " (" + selected_df['course_id'].astype(str) + ")"

    # Prepare the data source
    source = ColumnDataSource(selected_df)

    # Color map for categories
    color_map = factor_cmap('category', palette=[DARKER_ITAM_COLOR, ITAM_COLOR, LIGHTER_ITAM_COLOR], factors=['Peores', 'Promedio', 'Mejores'])

    # Create the figure
    p = figure(
        y_range=selected_df['course_id_str'][::-1],  # Reverse for descending order
        width=800,
        height=HEIGHT,
        title=f"Tiempo promedio de retroalimentación (mejores, promedio y peores {N})",
        toolbar_location='above',
        x_axis_label="Tiempo promedio de retroalimentación (días)",
        y_axis_label = "ID del curso",
        tools="pan,box_zoom,reset,save",
        margin=(20, 20, 20, 20),
    )

    # Add horizontal bars
    p.hbar(
        y='course_id_str', 
        right='avg_feedback_days', 
        height=0.4,
        color=color_map,
        source=source,
        legend_field='category'
    )

    # Add hover tool
    hover = HoverTool(
        tooltips=[
            ("Course ID", "@course_id"),
            ("Course name", "@course_name"),
            ("Avg Feedback Time (days)", "@avg_feedback_days{0.00}"),
            ("Category", "@category"),
        ]
    )
    p.add_tools(hover)

    # Add a vertical reference line for the average feedback time
    avg_line = Span(
        location=avg_feedback,
        dimension='height',
        line_color='black',
        line_dash='dotted',
        line_width=2
    )
    p.add_layout(avg_line)

    # Add a label for the average line
    avg_label = Label(
        x=avg_feedback + 1,
        y=len(selected_df['course_name']) - 1,
        text=f"Avg: {avg_feedback:.2f} days",
        text_font_size="10pt",
        text_color="black"
    )
    p.add_layout(avg_label)

    # Customize the legend
    p.legend.title = "Categoría"
    p.legend.location = "top_right"
    p.legend.orientation = "vertical"
    p.legend.click_policy = "hide"

    # Style the plot
    p.background_fill_color = "#f9f9f9"
    p.border_fill_color = "#ffffff"
    p.outline_line_color = None
    p.title.text_font_size = TEXT_FONT_SIZE

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
        height=HEIGHT,
        title=f"Tasa de finalización por curso (Mejores, promedio y peores {N})",
        x_axis_label="ID del curso",
        y_axis_label="Tasa de finalización (%)",
        toolbar_location="above",
        tools="pan,box_zoom,reset,save,hover",
        x_range=selected_df["course_id_str"],
        y_range=(0, 100),
        margin=(20, 0, 20, 0),

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
        text="Área inferior",
        text_color="gray",
        text_font_size="10pt",
        text_align="left",
        y_units='data'
    )
    mid_label = Label(
        x=10, y=avg_completion + 20,
        text="Área promedio",
        text_color="gray",
        text_font_size="10pt",
        text_align="left",
        y_units='data'
    )
    high_label = Label(
        x=10, y=mid_range_upper + label_y_offset,
        text="Área superior",
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
        text=f"Promedio total: {avg_completion:.2f}%",
        text_color="gray",
        text_font_size="10pt",
        text_align="center"
    )
    p.add_layout(avg_label)

    selected_df["category"] = (
    ["Mejores"] * len(top_n) +
    ["Peores"] * len(bottom_n) +
    ["Promedio"] * len(avg_courses)
    )

    # Updated colors for Spanish labels
    colors = {"Mejores": COLOR_FOR_BEST, "Peores": COLOR_FOR_WORST, "Promedio": COLOR_FOR_AVERAGE}
    for category, color in colors.items():
        category_source = ColumnDataSource(selected_df[selected_df["category"] == category])
        p.line(x="course_id_str", y="completion_rate", color=color, legend_label=category, source=category_source, line_width=2)
        p.scatter(x="course_id_str", y="completion_rate", size=6, color=color, legend_label=category, source=category_source)

    p.legend.title = "Categorías"
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    p.legend.background_fill_alpha = 0.6
    p.title.text_font_size = TEXT_FONT_SIZE

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

    # Create figure with a wider width for better bar spacing
    p = figure(
        x_range=course_ids,
        width=900,   # Increased width for better spacing
        height=HEIGHT,
        title="Cumplimiento de los objetivos de aprendizaje por curso",
        toolbar_location='above',
        tools=[hover, 'pan', 'box_zoom', 'wheel_zoom', 'save', 'reset'],
        margin=(20, 20, 20, 20)  # Add margin to accommodate the legend on the right
    )

    # Plot avg_achievement_percentage
    bar1 = p.vbar(
        x=dodge('course_id', -0.2, range=p.x_range), 
        top='avg_achievement_percentage', 
        width=0.25, 
        source=source,
        color=ITAM_COLOR,
        legend_label=f"Porcentaje de logro"
    )

    # Plot mastery_percentage
    bar2 = p.vbar(
        x=dodge('course_id', 0.2, range=p.x_range), 
        top='mastery_percentage', 
        width=0.25, 
        source=source,
        color=LIGHTER_ITAM_COLOR,
        legend_label=f"Porcentaje de dominio "
    )

    # Add average dotted lines
    p.line(
        x=p.x_range.factors, 
        y=[avg_achievement_avg] * len(p.x_range.factors),
        line_width=2, 
        line_dash="dotted", 
        color="blue",
        legend_label=f"Promedio de logro ({avg_achievement_avg:.1f}%)"
    )

    p.line(
        x=p.x_range.factors, 
        y=[mastery_percentage_avg] * len(p.x_range.factors),
        line_width=2, 
        line_dash="dotted", 
        color="green",
        legend_label=f"Promedio de dominio ({mastery_percentage_avg:.1f}%)"
    )

    # Customize appearance
    p.x_range.range_padding = 0.1
    p.y_range.start = 0
    p.xgrid.grid_line_color = None
    p.yaxis.axis_label = 'Porcentaje'
    p.xaxis.axis_label = 'ID del curso'
    p.xaxis.major_label_orientation = 1.2
    p.title.text_font_size = TEXT_FONT_SIZE

    # Configure legend to the right of the plot
    p.legend.location = "top_right"
    p.legend.orientation = "vertical"
    p.legend.label_text_font_size = "10pt"
    p.legend.border_line_color = "gray"
    p.legend.border_line_width = 1
    p.legend.padding = 5
    p.legend.spacing = 5
    p.legend.background_fill_alpha = 0.1
    p.add_layout(p.legend[0], 'right')

    # Make legend interactive
    p.legend.click_policy = "hide"

    return p



def create_students_retention_rate_plot(source, percentile=25):
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
        width=900,
        height=HEIGHT,
        title=f"Tasa de retención de estudiantes por curso ({100-percentile}%)",
        toolbar_location="right",
        x_axis_label="ID del curso",
        y_axis_label="Tasa de retención (%)"
    )
    
    # Create bars with the specified green color
    bars = p.vbar(
        x='course_id_str',
        top='retention_rate_percentage',
        width=0.7,
        source=filtered_source,
        fill_color=ITAM_COLOR,
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
    p.title.text_font_size = TEXT_FONT_SIZE
    
    # Compute statistics
    avg_retention = df['retention_rate_percentage'].mean()
    median_retention = df['retention_rate_percentage'].median()
    
    # Add statistics to the title
    p.title.text = (
        f"Tasa de retención de estudiantes por curso (Percentil {100-percentile}%)\n"
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
