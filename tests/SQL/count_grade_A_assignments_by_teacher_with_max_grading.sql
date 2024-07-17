WITH teacher_graded_counts AS (
    SELECT teacher_id, COUNT(*) as graded_count
    FROM assignments
    WHERE state = 'GRADED'
    GROUP BY teacher_id
),
max_graded_teacher AS (
    SELECT teacher_id
    FROM teacher_graded_counts
    WHERE graded_count = (SELECT MAX(graded_count) FROM teacher_graded_counts)
    LIMIT 1
)
SELECT COUNT(*) 
FROM assignments a
JOIN max_graded_teacher mgt ON a.teacher_id = mgt.teacher_id
WHERE a.state = 'GRADED' AND a.grade = 'A';