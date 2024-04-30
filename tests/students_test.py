from core.models.assignments import AssignmentStateEnum, GradeEnum
from core.models.students import Student

def test_get_assignments_student_1(client, h_student_1):
    response = client.get(
        '/student/assignments',
        headers=h_student_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 1


def test_get_assignments_student_2(client, h_student_2):
    response = client.get(
        '/student/assignments',
        headers=h_student_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['student_id'] == 2


def test_post_assignment_null_content(client, h_student_1):
    """
    failure case: content cannot be null
    """

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': None
        })

    assert response.status_code == 400


def test_post_assignment_student_1(client, h_student_1):
    content = 'ABCD TESTPOST'

    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': content
        })

    assert response.status_code == 200

    data = response.json['data']
    draft_assignment_id = data['id']  # Save the assignment ID
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None
    return draft_assignment_id


def test_submit_assignment_student_1(client, h_student_1):
    assignment_id = test_post_assignment_student_1(client, h_student_1)  # Get the assignment ID
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': assignment_id,
            'teacher_id': 2
        })

    assert response.status_code == 200

    data = response.json['data']
    submitted_assignment_id = data['id']  # Save the assignment ID
    assert data['student_id'] == 1
    assert data['state'] == 'SUBMITTED'
    assert data['teacher_id'] == 2
    return submitted_assignment_id


def test_assignment_resubmit_error(client, h_student_1):
    assignment_id = test_submit_assignment_student_1(client, h_student_1)
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': assignment_id,
            'teacher_id': 2
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'only a draft assignment can be submitted'


def test_grade_assignment(client, h_teacher_2,h_student_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            'id': test_submit_assignment_student_1(client,h_student_1),
            'grade': GradeEnum.C.value
        }
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_student_repr(client,h_student_1):
    student = Student.query.first()
    assert repr(student) == '<Student {}>'.format(student.id)
    