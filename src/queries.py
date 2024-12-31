def get_progress_in_course_requirements_query(semester_start_date, semester_end_date):
    return f"""
    WITH enrolled_students AS (
        SELECT DISTINCT 
            e.user_id,
            e.course_id
        FROM canvas.enrollments e
        JOIN canvas.courses c ON e.course_id = c.id
        WHERE e.type = 'StudentEnrollment'
          AND e.workflow_state NOT IN ('deleted', 'rejected', 'inactive')
          AND (
              -- Either the enrollment has specific dates that overlap with the semester
              (
                  (e.start_at IS NULL OR e.start_at <= '{semester_end_date}'::timestamp)
                  AND (e.end_at IS NULL OR e.end_at   >= '{semester_start_date}'::timestamp)
                  AND (e.end_at IS NULL OR e.start_at IS NULL OR e.end_at >= e.start_at)
              )

          )
    ),
    module_progress AS (
        SELECT 
            es.user_id,
            es.course_id,
            cmp.workflow_state,
            COUNT(*) AS module_count
        FROM enrolled_students es
        JOIN canvas.context_modules cm ON cm.context_id = es.course_id
        LEFT JOIN canvas.context_module_progressions cmp 
              ON cmp.context_module_id = cm.id 
            AND cmp.user_id = es.user_id
        GROUP BY es.user_id, es.course_id, cmp.workflow_state
    ),
    course_completion AS (
        SELECT 
            course_id,
            ROUND(
                COUNT(CASE WHEN workflow_state = 'completed' THEN 1 END) * 100.0 
                / NULLIF(COUNT(*), 0),
                2
            ) AS completion_percentage
        FROM module_progress
        GROUP BY course_id
    )
    SELECT *
    FROM course_completion
    WHERE completion_percentage > 0.0;
    """


def get_feedback_time_by_course_query(semester_start_date: str, semester_end_date: str) -> str:
    return f"""
    WITH submission_feedback AS (
      SELECT 
        s.id AS submission_id,
        s.course_id,
        s.submitted_at,
        MIN(sc.created_at) AS first_feedback_time
      FROM canvas.submissions s
      LEFT JOIN canvas.submission_comments sc ON s.id = sc.submission_id
      WHERE s.submitted_at IS NOT NULL
        AND (sc.author_id IS NULL OR sc.author_id != s.user_id)
        AND (s.submitted_at >= '{semester_start_date}'::timestamp)
        AND (s.submitted_at <= '{semester_end_date}'::timestamp)
      GROUP BY s.id, s.course_id, s.submitted_at
    ),
    feedback_analysis AS (
      SELECT
        sf.course_id,
        CASE
          WHEN sf.first_feedback_time IS NULL THEN 30 -- assign 30 days for missing feedback
          WHEN sf.first_feedback_time >= sf.submitted_at THEN 
            EXTRACT(EPOCH FROM (sf.first_feedback_time - sf.submitted_at)) / 86400 -- secs in a day 
          ELSE NULL -- for invalid data
        END AS feedback_time_in_days
      FROM submission_feedback sf
    )
    SELECT 
      course_id,
      ROUND(AVG(feedback_time_in_days), 2) AS avg_feedback_days
    FROM feedback_analysis
    WHERE feedback_time_in_days IS NOT NULL
    GROUP BY course_id
    ORDER BY avg_feedback_days ASC;
    """


def get_course_completion_rate_query(semester_start_date: str, semester_end_date: str) -> str:
    return f"""
WITH active_courses AS (
    SELECT id AS course_id
    FROM canvas.courses c
    WHERE c.workflow_state = 'available'
    AND (
        (c.start_at IS NULL OR c.start_at <= '{semester_start_date}'::timestamp)
    )
),
course_requirements AS (
    SELECT 
        course_id,
        COUNT(DISTINCT cm.id) as total_modules
    FROM active_courses ac
    JOIN canvas.context_modules cm ON cm.context_id = ac.course_id
    WHERE cm.workflow_state = 'active'
    GROUP BY course_id
),
student_progress AS (
    SELECT 
        e.course_id,
        e.user_id,
        COUNT(DISTINCT CASE WHEN cmp.workflow_state = 'completed' 
              THEN cm.id END) as completed_modules
    FROM active_courses ac
    JOIN canvas.enrollments e ON e.course_id = ac.course_id
    JOIN canvas.context_modules cm ON cm.context_id = e.course_id
    LEFT JOIN canvas.context_module_progressions cmp 
        ON cmp.context_module_id = cm.id 
        AND cmp.user_id = e.user_id
    WHERE e.type = 'StudentEnrollment'
    AND e.workflow_state NOT IN ('deleted', 'rejected', 'inactive')
    AND (
        (e.start_at IS NULL OR e.start_at <= '{semester_end_date}'::timestamp)
        AND (e.end_at IS NULL OR e.end_at >= '{semester_start_date}'::timestamp)
    )
    GROUP BY e.course_id, e.user_id
)
SELECT 
    sp.course_id,
    COUNT(DISTINCT sp.user_id) as total_enrolled,
    COUNT(DISTINCT CASE 
        WHEN sp.completed_modules >= cr.total_modules THEN sp.user_id 
    END) as completed_count,
    ROUND(
        COUNT(DISTINCT CASE 
            WHEN sp.completed_modules >= cr.total_modules THEN sp.user_id 
        END)::numeric * 100.0 / 
        NULLIF(COUNT(DISTINCT sp.user_id), 0),
        2
    ) as completion_rate
FROM student_progress sp
JOIN course_requirements cr ON cr.course_id = sp.course_id
GROUP BY sp.course_id;
    """


def get_learning_objective_completion_query(semester_start_date: str, semester_end_date: str) -> str:
    return f"""
    WITH outcome_results AS (
        SELECT
            lor.learning_outcome_id,
            lor.context_id AS course_id,
            lor.user_id,
            lor.score,
            lor.possible,
            lor.mastery
        FROM canvas.learning_outcome_results lor
        WHERE lor.workflow_state = 'active'
          AND lor.created_at >= '{semester_start_date}'::timestamp
          AND lor.created_at <= '{semester_end_date}'::timestamp
    ),
    course_aggregates AS (
        SELECT
            course_id,
            COUNT(DISTINCT user_id) AS total_students,
            COUNT(DISTINCT CASE WHEN mastery THEN user_id END) AS mastered_count,
            ROUND(
                AVG(
                    CASE WHEN possible > 0 THEN (score / possible * 100)
                         ELSE NULL
                    END
                )::numeric,
                2
            ) AS avg_achievement_percentage,
            ROUND(
                (
                    COUNT(DISTINCT CASE WHEN mastery THEN user_id END) * 100.0 /
                    NULLIF(COUNT(DISTINCT user_id), 0)
                )::numeric,
                2
            ) AS mastery_percentage
        FROM outcome_results
        GROUP BY course_id
    )
    SELECT
        course_id,
        total_students,
        mastered_count,
        avg_achievement_percentage,
        mastery_percentage
    FROM course_aggregates
    ORDER BY mastery_percentage DESC;
    """


def get_course_retention_query(semester_start_date, semester_end_date):
    """
    Get SQL query for course retention rates within a semester period.
    Both initial and final enrollment counts are taken from the same time frame.
    
    Args:
        semester_start_date (str): Start date in format 'YYYY-MM-DD'
        semester_end_date (str): End date in format 'YYYY-MM-DD'
        
    Returns:
        str: SQL query with parameters replaced
    """
    return f"""
    WITH enrollment_counts AS (
      SELECT
        e.course_id,
        c.name as course_name,
        COUNT(DISTINCT CASE
          WHEN e.created_at BETWEEN '{semester_start_date}'::timestamp AND '{semester_end_date}'::timestamp
          AND e.workflow_state = 'active'
          THEN e.user_id
        END) as initial_enrollment,
        COUNT(DISTINCT CASE
          WHEN e.created_at BETWEEN '{semester_start_date}'::timestamp AND '{semester_end_date}'::timestamp
          AND e.workflow_state = 'active'
          AND e.updated_at BETWEEN '{semester_start_date}'::timestamp AND '{semester_end_date}'::timestamp
          THEN e.user_id
        END) as final_enrollment
      FROM
        canvas.enrollments e
        JOIN canvas.courses c ON e.course_id = c.id
      WHERE
        e.type = 'StudentEnrollment'
        AND c.workflow_state = 'available'
      GROUP BY
        e.course_id,
        c.name
    )
    SELECT
      course_id,
      course_name,
      initial_enrollment,
      final_enrollment,
      CASE
        WHEN initial_enrollment > 0 THEN
          ROUND(
            CAST(final_enrollment AS numeric) /
            CAST(initial_enrollment AS numeric) * 100,
            2
          )
        ELSE 0
      END as retention_rate
    FROM
      enrollment_counts
    WHERE
      initial_enrollment > 0
    ORDER BY
      retention_rate DESC;
    """

