SELECT COUNT(*) AS grade_A_count
FROM assignments
WHERE grade = 'A' AND teacher_id = (
    SELECT teacher_id
    FROM assignments
    WHERE grade = 'A'
    GROUP BY teacher_id
    ORDER BY COUNT(*) DESC
    LIMIT 1
);