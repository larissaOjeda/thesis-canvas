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
              (e.start_at IS NULL OR e.start_at <= '{semester_end_date}'::timestamp)
              AND (e.end_at IS NULL OR e.end_at   >= '{semester_start_date}'::timestamp)
              AND (e.end_at IS NULL OR e.start_at IS NULL OR e.end_at >= e.start_at)
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
            c.id as course_id,
            c.name as course_name,
            ROUND(
                COUNT(CASE WHEN mp.workflow_state = 'completed' THEN 1 END) * 100.0 
                / NULLIF(COUNT(*), 0),
                2
            ) AS completion_percentage
        FROM canvas.courses c
        LEFT JOIN module_progress mp ON mp.course_id = c.id
        GROUP BY c.id, c.name
    )
    SELECT *
    FROM course_completion
    WHERE completion_percentage > 0.0
    ORDER BY completion_percentage ASC;
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
      fa.course_id,
      c.name AS course_name,
      ROUND(AVG(fa.feedback_time_in_days), 2) AS avg_feedback_days
    FROM feedback_analysis fa
    JOIN canvas.courses c ON fa.course_id = c.id
    WHERE fa.feedback_time_in_days IS NOT NULL
    GROUP BY fa.course_id, c.name
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

def get_learning_objective_completion_query(semester_start_date, semester_end_date): 
    return f"""WITH outcome_results AS (
    SELECT
        lor.learning_outcome_id,
        lor.context_id AS course_id,
        lor.score,
        lor.possible,
        lor.mastery
    FROM canvas.learning_outcome_results lor
    WHERE lor.context_type = 'Course'
    AND lor.created_at <= '{semester_end_date}'::timestamp
    and lor.created_at >= '{semester_start_date}'::timestamp
),
course_aggregates AS (
    SELECT
        course_id,
        ROUND(
            AVG(CASE WHEN possible > 0 THEN (score / possible * 100) ELSE NULL END)::numeric,
            2
        ) AS avg_achievement_percentage,
        ROUND(
            (COUNT(CASE WHEN mastery THEN 1 END) * 100.0 / COUNT(*))::numeric,
            2
        ) AS mastery_percentage
    FROM outcome_results
    GROUP BY course_id
)
SELECT
    ca.course_id,
    c.name AS course_name,
    ca.avg_achievement_percentage,
    ca.mastery_percentage
FROM course_aggregates ca
JOIN canvas.courses c ON ca.course_id = c.id
ORDER BY ca.mastery_percentage DESC;
"""


def get_course_retention_query(semester_start_date, semester_end_date, enrollment_term_name):
    return f"""
WITH EnrollmentCounts AS (
    SELECT 
        c.id AS course_id,
        c.name AS course_name,
        et.name AS term_name,
        -- Total enrollments
        COUNT(DISTINCT CASE 
            WHEN e.type = 'StudentEnrollment' 
            THEN e.user_id 
        END) AS total_enrollments,  
        -- Active enrollments (enrolled and active during semester)
        COUNT(DISTINCT CASE 
            WHEN e.type = 'StudentEnrollment'
                 AND e.created_at >= '{semester_start_date}'::timestamp  -- start semester
                 AND e.last_activity_at BETWEEN
                     '{semester_end_date}'::timestamp - INTERVAL '3 days'
                     AND '{semester_end_date}'::timestamp + INTERVAL '3 days'
            THEN e.user_id
        END) AS active_enrollments
    FROM canvas.courses c
    JOIN canvas.enrollments e 
      ON c.id = e.course_id
    JOIN canvas.enrollment_terms et 
      ON c.enrollment_term_id = et.id
    WHERE e.type = 'StudentEnrollment'
    AND et.name ILIKE '%%{enrollment_term_name}%%'
    GROUP BY c.id, c.name, et.name
)
SELECT 
    course_id,
    course_name,
    term_name,
    total_enrollments,
    active_enrollments,
    ROUND(
        (active_enrollments::DECIMAL / NULLIF(total_enrollments, 0) * 100)::DECIMAL, 
        2
    ) AS retention_rate_percentage
FROM EnrollmentCounts
WHERE total_enrollments > 0
AND active_enrollments > 0
ORDER BY retention_rate_percentage DESC;
"""
