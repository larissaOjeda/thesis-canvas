import numpy as np

def plot_score_distribution(submissions_df, year, semester):
    # Filter submissions for valid scores
    valid_submissions = submissions_df[submissions_df['value.score'].notna()]

    # Extract scores
    scores = valid_submissions['value.score']

    # Create histogram data
    hist, edges = np.histogram(scores, bins=10, range=[scores.min(), scores.max()])

    return hist, edges

