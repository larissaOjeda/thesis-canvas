from datetime import datetime, date
import numpy as np
import pandas as pd 

from bokeh.models import ColumnDataSource, DataTable, TableColumn, Label, Span, HoverTool, HTMLTemplateFormatter
from bokeh.plotting import figure


translation_map = {
    "Spring": "Primavera", 
    "Summer": "Verano", 
    "Winter": "Invierno"
}

def get_semester_in_spanish(semester): 
    if semester in translation_map.keys():
        return translation_map[semester]
    else:
        return f"Invalid period, the available periods are: Summer, Spring and Winter"

def get_semester_dates(year, semester):
    """
    Returns the start and end date of the semester as strings in YYYY-MM-DD format.
    """
    if semester == 'Spring':
        return f'{year}-01-03', f'{year}-06-01'
    elif semester == 'Summer':
        return f'{year}-06-02', f'{year}-08-05'
    elif semester == 'Winter':
        return f'{year}-08-15', f'{year}-12-25'
    else:
        raise ValueError("Invalid semester. Choose between 'Spring', 'Summer', or 'Winter'.")


def get_semester_months(year, semester):
    if semester == "Spring":
        start_date = datetime(year, 1, 3)  # january 3rd 
        end_date = datetime(year, 6, 1)
    elif semester == "Summer":
        start_date = datetime(year, 6, 2)  # august 2nd
        end_date = datetime(year, 8, 5)
    elif semester == "Fall":
        start_date = datetime(year, 8, 15) # august 15th 
        end_date = datetime(year, 12, 25)
    else:
        raise ValueError("Invalid semester")

    months = pd.date_range(start_date, end_date, freq='MS').strftime('%b').tolist()
    return months

def get_semester_term(semester_start_date: str) -> str: 
    start = datetime.strptime(semester_start_date, '%Y-%m-%d').date()
    year = start.year

    spring_start = date(year, 1, 1)   # january 1st
    spring_end = date(year, 6, 1)     # june 1st 

    summer_start = date(year, 6, 15)  # june 15th
    summer_end = date(year, 8, 10)    # august 10th 

    fall_start = date(year, 8, 15)    # august 15th 
    fall_end = date(year, 12, 25)     # december 25th

    if spring_start <= start <= spring_end:
        return f"PRIMAVERA {year} LICENCIATURA"
    elif summer_start <= start <= summer_end:
        return f"VERANO {year}"
    elif fall_start <= start <= fall_end:
        return f"OTOÑO {year} LICENCIATURA"
    else:
        return f"Default term"

def get_current_semester():
    month = datetime.now().month
    if 1 <= month <= 6:
        return "Spring"
    elif 7 <= month <= 12:
        return "Fall"
    else:
        raise ValueError("Invalid month for semester calculation.")


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
        toolbar_location='right',
        toolbar_sticky=True,
        tools='pan,box_zoom,reset,save'
    )
    
    p.quad(
        top='top', 
        bottom=0,
        left='left',
        right='right',
        source=hist_source,
        fill_color=fill_color,
        line_color='#019b7a',
        alpha=alpha
    )

    # Add hover functionality for the bars
    hover = HoverTool(
        tooltips=[
            ('Count', '@top'),
        ],
        mode='vline'  # Show hover when moving vertically in the same bin
    )
    p.add_tools(hover)

    # Add average line
    avg_value = df[col_name].mean()
    avg_line = Span(
        location=avg_value,
        dimension='height',
        line_color='gray',
        line_dash='dotted',
        line_width=1.5,
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
        fill_color='#019b7a',
        alpha=0.85,
        width=400,
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


def create_completion_table(source):
    """
    Creates a Bokeh DataTable showing course completion percentages with color indicators
    """
    df = source.to_df()

    # Standardize and clean the 'course_name' column
    df['course_name'] = df['course_name'].str.strip()  # Remove leading/trailing spaces
    df['course_name'] = df['course_name'].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')  # Remove accents
    df['course_name'] = df['course_name'].str.title()  # Convert to title case
    df = df[~df['course_name'].str.contains('Leccion', case=False, na=False)]

    df = df.sort_values('completion_percentage', ascending=True)

    source = ColumnDataSource(df)

    # Create HTML template for color-coded completion percentage
    template = """
    <div style="background:<%= 
        value < 40 ? '#ffcccc' :  /* Light red for low completion */
        value < 70 ? '#dceeff' :  /* Light blue for medium completion */
        '#d4f4cc'                /* Soft green for high completion */
    %>; padding: 2px 5px; border-radius: 3px;">
        <%= value.toFixed(2) %>%
    </div>
    """

    # Define the columns for the table
    columns = [
        TableColumn(field="course_name", title="Course Name", width=250),
        TableColumn(field="course_id", title="Course ID", width=100),
        TableColumn(
            field="completion_percentage",
            title="Completion %",
            formatter=HTMLTemplateFormatter(template=template),
            width=150
        )
    ]

    # Create the DataTable
    data_table = DataTable(
        source=source,
        columns=columns,
        width=600,
        height=350,
        index_position=None,
        sortable=True,
        reorderable=False,
    )

    return data_table
