import pandas as pd 
import os
from dotenv import load_dotenv

from sqlalchemy import create_engine

from bokeh.io import save, output_file
from bokeh.layouts import column, row
from bokeh.models import (
    ColumnDataSource, 
    Spacer,
)

import queries 
import plots
from utils import helpers


load_dotenv() 
DATABASE_URL = os.environ.get("DATABASE_URL")

def update_data(year, semester, engine):
    """
    Updates the data based on selected year and semester.
    """
    semester_start_date, semester_end_date = helpers.get_semester_dates(year, semester)
    
    course_reqs_progress = queries.get_progress_in_course_requirements_query(semester_start_date, semester_end_date)
    course_reqs_progress_df = pd.read_sql(course_reqs_progress, engine)
    
    feedback_query = queries.get_feedback_time_by_course_query(semester_start_date, semester_end_date)
    feedback_df = pd.read_sql(feedback_query, engine)
    feedback_df['circle_size'] = feedback_df['avg_feedback_days'] * 2  # Add circle size column for scatter plot

    completion_rate_query = queries.get_course_completion_rate_query(semester_start_date, semester_end_date)
    completion_rate_df = pd.read_sql(completion_rate_query, engine)

    learning_objective_completion_query = queries.get_learning_objective_completion_query(semester_start_date, semester_end_date)
    learning_objective_df = pd.read_sql(learning_objective_completion_query, engine)

    term = helpers.get_semester_term(semester_start_date)
    student_retention_query = queries.get_course_retention_query(semester_start_date, semester_end_date, term)
    student_retention_df = pd.read_sql(student_retention_query, engine)
    
    return (
        ColumnDataSource(course_reqs_progress_df), 
        ColumnDataSource(feedback_df), 
        ColumnDataSource(completion_rate_df),
        ColumnDataSource(learning_objective_df),
        ColumnDataSource(student_retention_df)
    )


def save_dashboard(year, semester, filename='course_completion_dashboard.html'):
    """
    Saves a static version of the dashboard for a specific year and semester.
    """
    engine = create_engine(DATABASE_URL)
    
    completion_source, feedback_source, completion_rate_source, learning_objective_source, student_retention_source = update_data(year, semester, engine)
    
    title = f"Course Completion and Feedback Dashboard - {semester} {year}"
    
    layout = column(
    row(
        plots.create_students_retention_rate_plot(student_retention_source),
        helpers.create_completion_distribution(completion_source),
        Spacer(width=50),
        helpers.create_completion_table(completion_source),
    ),
    row(
        plots.plot_learning_objective_completion(learning_objective_source),
        plots.create_course_completion_rate(completion_rate_source), 
        plots.create_feedback_scatter(feedback_source),
    ), 
    )
    
    output_file(filename, title=title)
    save(layout)
    print(f"Dashboard saved as {filename}")

import argparse

def main():
    parser = argparse.ArgumentParser(description="Process semester and year input.")
    parser.add_argument(
        "-s", "--semester", type=str, required=True,
        help="Specify the semester (e.g., PRIMAVERA, OTOÑO)"
    )
    parser.add_argument(
        "-y", "--year", type=int, required=True,
        help="Specify the year (e.g., 2024)"
    )

    args = parser.parse_args()

    semester = args.semester
    year = args.year

    if year < 2000 or year > 2100:
        print("Year must be between 2000 and 2100. Exiting...")
        return

    print(f"Processing data for semester: {semester} {year}")

    filename = f'course_completion_dashboard_{semester.lower()}_{year}.html'
    save_dashboard(year, semester, filename)
    


if __name__ == "__main__":
    main()
