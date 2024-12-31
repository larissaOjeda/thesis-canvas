from datetime import datetime
import numpy as np
import pandas as pd 

from bokeh.models import ColumnDataSource, DataTable, TableColumn, Label, Span
from bokeh.plotting import figure


def get_semester_dates(year, semester):
    """
    Returns the start and end date of the semester as strings in YYYY-MM-DD format.
    """
    if semester == 'Spring':
        return f'{year}-01-01', f'{year}-06-30'
    elif semester == 'Summer':
        return f'{year}-06-01', f'{year}-07-31'
    elif semester == 'Winter':
        return f'{year}-08-01', f'{year}-12-31'
    else:
        raise ValueError("Invalid semester. Choose between 'Spring', 'Summer', or 'Winter'.")


def get_semester_months(year, semester):
    if semester == "Spring":
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 6, 30)
    elif semester == "Summer":
        start_date = datetime(year, 6, 1)
        end_date = datetime(year, 8, 31)
    elif semester == "Fall":
        start_date = datetime(year, 9, 1)
        end_date = datetime(year, 12, 31)
    else:
        raise ValueError("Invalid semester")

    months = pd.date_range(start_date, end_date, freq='MS').strftime('%b').tolist()
    return months


def create_summary_table(
    source,
    col_name: str,
    label: str = '',
    suffix: str = '',
    empty_message: str = 'No Data'
):
    """
    Creates a summary statistics table for a given column in the source.
    
    :param source: ColumnDataSource containing your data
    :param col_name: The name of the numeric column to compute stats on
    :param label: A short label used in the row titles. 
                  E.g. 'Completion' or 'Feedback Time'
    :param suffix: A string appended to numeric stats, 
                   e.g. '%' or ' days'
    :param empty_message: Message to display if no data is present
    
    :return: DataTable object
    """
    df = source.to_df()

    if df.empty or col_name not in df.columns or df[col_name].dropna().empty:
        # If no data or the column doesn't exist or all nulls
        stats_df = pd.DataFrame({
            'Metric': [empty_message],
            'Value': ['N/A']
        })
    else:
        stats_df = pd.DataFrame({
            'Metric': [
                f'Avg {label}',
                f'Med {label}',
                f'Min {label}',
                f'Max {label}',
                f'Total Courses'
            ],
            'Value': [
                f"{df[col_name].mean():.1f}{suffix}",
                f"{df[col_name].median():.1f}{suffix}",
                f"{df[col_name].min():.1f}{suffix}",
                f"{df[col_name].max():.1f}{suffix}",
                f"{len(df)}"
            ]
        })

    table_source = ColumnDataSource(stats_df)

    columns = [
        TableColumn(field='Metric', title='Metric'),
        TableColumn(field='Value', title='Value')
    ]

    data_table = DataTable(
        source=table_source,
        columns=columns,
        width=200,
        height=200,
        index_position=None
    )
    return data_table


def create_histogram(
    source,
    col_name: str,
    title: str = 'Distribution',
    bins: int = 20,
    bin_range: tuple = None,
    fill_color: str = 'navy',
    alpha: float = 0.5,
    width: int = 400,
    height: int = 300,
    x_axis_label: str = '',
    y_axis_label: str = 'Number of Courses',
    label_text: str = '',
):
    """
    Creates a generic histogram for any numeric column in the source DataFrame.

    :param source: Bokeh ColumnDataSource containing your data
    :param col_name: Name of the numeric column to histogram
    :param title: Plot title
    :param bins: Number of bins in the histogram
    :param bin_range: Tuple specifying (min, max) range for the histogram
    :param fill_color: Bar color for the histogram
    :param alpha: Transparency for the bars
    :param width: Width of the plot
    :param height: Height of the plot
    :param x_axis_label: Label for the x-axis
    :param y_axis_label: Label for the y-axis
    :param label_text: Text displayed as a label inside the plot
    :return: A Bokeh figure object
    """
    df = source.to_df()

    if df.empty or col_name not in df.columns or df[col_name].dropna().empty:
        p_empty = figure(width=width, height=height, title=f'No Data for {col_name}')
        return p_empty

    hist, edges = np.histogram(
        df[col_name], 
        bins=bins, 
        range=bin_range
    )

    hist_source = ColumnDataSource({
        'top': hist,
        'left': edges[:-1],
        'right': edges[1:]
    })
    
    p = figure(
        width=width,
        height=height,
        title=title,
        toolbar_location='above',
        tools='pan,box_zoom,reset,save'
    )
    
    p.quad(
        top='top', 
        bottom=0,
        left='left',
        right='right',
        source=hist_source,
        fill_color=fill_color,
        alpha=alpha
    )

    # Add average line
    avg_value = df[col_name].mean()
    avg_line = Span(
        location=avg_value,
        dimension='height',
        line_color='gray',
        line_dash='dotted',
        line_width=2,
    )
    p.add_layout(avg_line)

    # Add label for average line
    avg_label = Label(
        x=avg_value,
        y=max(hist) * 0.95,  # Position the label slightly below the top of the highest bar
        text=f"Avg: {avg_value:.2f}",
        text_font_size="10pt",
        text_color="gray",
        text_align="center"
    )
    p.add_layout(avg_label)

    # Optionally add a label inside the figure  
    # (placed at ~10% below max height, near left side)
    if hist.max() > 0:
        p.add_layout(Label(
            x=(edges[0] + edges[-1]) / 2,  # approximate center
            y=hist.max() * 0.9,
            text=label_text,
            text_font_size='10pt',
            text_alpha=0.6,
            text_align='center'
        ))
    
    p.xaxis.axis_label = x_axis_label
    p.yaxis.axis_label = y_axis_label
    
    return p




def create_completion_distribution(source):
    return create_histogram(
        source=source,
        col_name='completion_percentage',
        title='Distribution of Completion Percentages',
        bins=20,
        bin_range=(0, 100),           # completion % typically 0–100
        fill_color='navy',
        alpha=0.5,
        width=700,
        height=400,
        x_axis_label='Completion Percentage (%)',
        y_axis_label='Number of Courses',
        # label_text='Completion Distribution'
    )


def create_feedback_distribution(source):
    return create_histogram(
        source=source,
        col_name='avg_feedback_days',
        title='Distribution of Feedback Times',
        bins=10,
        bin_range=None,               # automatically computed from data
        fill_color='firebrick',
        alpha=0.6,
        width=400,
        height=300,
        x_axis_label='Average Feedback Time (Days)',
        y_axis_label='Number of Courses',
        label_text='Feedback Distribution'
    )


def create_completion_summary(source):
    return create_summary_table(
        source=source,
        col_name='completion_percentage',
        label='Completion',
        suffix='%',
        empty_message='No Completion Data'
    )

def create_feedback_summary(source):
    return create_summary_table(
        source=source,
        col_name='avg_feedback_days',
        label='Feedback Time',
        suffix=' days',
        empty_message='No Feedback Data'
    )

