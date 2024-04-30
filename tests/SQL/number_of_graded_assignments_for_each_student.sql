-- Write query to get number of graded assignments for each student:
SELECT
    s.id AS student_id,
    COUNT(a.id) AS num_graded_assignments
FROM
    students s
JOIN
    assignments a ON s.id = a.student_id
WHERE
    a.state = 'GRADED'
GROUP BY
    s.id;