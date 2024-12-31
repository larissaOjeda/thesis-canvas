from bokeh.io import curdoc
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, DataTable, TableColumn, NumberFormatter, Button, DatePicker
from bokeh.plotting import figure
import pandas as pd
from datetime import date
from kpi import execute_module_completion_query
from bokeh.models import ColumnDataSource, HoverTool


def create_module_completion_rate_stats(start_date: str, end_date: str):
    """
    Creates the visualization components for module completion data
    """
    results = execute_module_completion_query(start_date, end_date)
    
    df = pd.DataFrame(results, columns=['course_id', 'completion_percentage'])
    df['completion_percentage'] = df['completion_percentage'].astype(float)
    print(df.describe())
    return df, df.describe()

def make_plot(df):
    """
    Creates the bar plot with tools for panning, zooming, saving, 
    and a hover tool to show details.
    """
    source = ColumnDataSource(df)

    p = figure(
        x_range=[str(x) for x in df['course_id']],
        height=400,
        title='Module Completion Rates by Course',
        toolbar_location="above", 
        tools="pan,box_zoom,wheel_zoom,reset,save,hover"
    )
    
    # Create the bar glyph
    p.vbar(
        x='course_id',
        top='completion_percentage',
        width=0.7,
        source=source,
        fill_color='#1f77b4',
        line_color='#1f77b4'
    )
    
    # Configure the hover tool
    hover = p.select_one(HoverTool)
    hover.tooltips = [
        ("Course ID", "@course_id"),
        ("Completion %", "@completion_percentage{0.2f}")
    ]
    hover.mode = 'vline'  # or 'mouse', depending on desired behavior
    
    # Additional plot settings
    p.xgrid.grid_line_color = None
    p.xaxis.axis_label = 'Course ID'
    p.yaxis.axis_label = 'Completion Rate (%)'
    p.xaxis.major_label_orientation = 45
    
    return p, source

def make_stats_table(stats_df):
    stats_source = ColumnDataSource(stats_df.round(2))
    
    columns = [
        TableColumn(field="index", title="Statistic"),
        TableColumn(
            field="Value", 
            title="Value (%)", 
            formatter=NumberFormatter(format="0.00")
        )
    ]
    
    stats_table = DataTable(
        source=stats_source,
        columns=columns,
        width=300,
        height=200,
        index_position=None
    )
    
    return stats_table, stats_source

def update():
    start = start_picker.value
    end = end_picker.value
    
    if start and end:
        start_str = start.strftime('%Y-%m-%d')
        end_str = end.strftime('%Y-%m-%d')
        
        df, stats_df = create_module_completion_rate_stats(start_str, end_str)
        
        # Update plot
        plot_source.data = ColumnDataSource(df).data
        p.x_range.factors = [str(x) for x in df['course_id']]
        
        # Update stats
        stats_source.data = ColumnDataSource(stats_df.round(2)).data

# Create initial data
initial_start = date(2024, 1, 1)
initial_end = date(2024, 6, 30)
df, stats = create_module_completion_rate_stats(
    initial_start.strftime('%Y-%m-%d'),
    initial_end.strftime('%Y-%m-%d')
)

# Create components
p, plot_source = make_plot(df)
stats_table, stats_source = make_stats_table(stats)

# Create date pickers
start_picker = DatePicker(title='Start Date', value=initial_start, min_date=date(2020, 1, 1))
end_picker = DatePicker(title='End Date', value=initial_end, min_date=date(2020, 1, 1))

# Create update button
update_button = Button(label='Update Visualization', button_type='primary')
update_button.on_click(update)

# Create layout
inputs = column(start_picker, end_picker, update_button, margin=(10, 10, 10, 10))
layout = column(
    row(inputs, stats_table),
    p
)

# Add to document
curdoc().add_root(layout)
curdoc().title = "Module Completion Dashboard"