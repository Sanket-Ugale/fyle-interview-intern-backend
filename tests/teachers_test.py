import json
from core import db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum

def test_get_assignments_teacher_1(client, h_teacher_1):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_1
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 1


def test_get_assignments_teacher_2(client, h_teacher_2):
    response = client.get(
        '/teacher/assignments',
        headers=h_teacher_2
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['teacher_id'] == 2
        assert assignment['state'] in ['SUBMITTED', 'GRADED']


def test_grade_assignment_cross(client, h_teacher_2):
    """
    failure case: assignment 1 was submitted to teacher 1 and not teacher 2
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": 1,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_bad_grade(client, h_teacher_1):
    """
    failure case: API should allow only grades available in enum
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "AB"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'ValidationError'


def test_grade_assignment_bad_assignment(client, h_teacher_1):
    """
    failure case: If an assignment does not exists check and throw 404
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 100000,
            "grade": "A"
        }
    )

    assert response.status_code == 404
    data = response.json

    assert data['error'] == 'FyleError'


def test_grade_assignment_draft_assignment(client, h_teacher_1):
    """
    failure case: only a submitted assignment can be graded
    """
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1
        , json={
            "id": 2,
            "grade": "A"
        }
    )

    assert response.status_code == 400
    data = response.json

    assert data['error'] == 'FyleError'

def test_get_assignments_without_authentication(client):
    response = client.get('/teacher/assignments')
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden

def test_grade_assignment_without_authentication(client):
    response = client.post(
        '/teacher/assignments/grade',
        json={
            "id": 1,
            "grade": "A"
        }
    )
    assert response.status_code in [401, 403]  # Either unauthorized or forbidden

def test_grade_assignment_state_transition(client, h_teacher_1, h_student_1):
    create_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': 'Assignment for grading test'
        })
    assert create_response.status_code == 200
    new_assignment_id = create_response.json['data']['id']

    submit_response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            "id": new_assignment_id,
            "teacher_id": 1
        }
    )
    assert submit_response.status_code == 200

    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": new_assignment_id,
            "grade": GradeEnum.A.value
        }
    )
    assert response.status_code == 200
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.A.value

def test_grade_nonexistent_assignment(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 9999,
            "grade": GradeEnum.A.value
        }
    )
    assert response.status_code == 404

def test_grade_assignment_invalid_grade(client, h_teacher_1):
    response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": 1,
            "grade": "INVALID_GRADE"
        }
    )
    assert response.status_code == 400

def test_teacher_grade_already_graded_assignment(client, h_teacher_1):
    # Create a new assignment
    create_response = client.post(
        '/student/assignments',
        headers={'X-Principal': json.dumps({"student_id": 1, "user_id": 1})},
        json={
            'content': 'Test assignment'
        })
    assert create_response.status_code == 200
    new_assignment_id = create_response.json['data']['id']

    # Submit the assignment
    submit_response = client.post(
        '/student/assignments/submit',
        headers={'X-Principal': json.dumps({"student_id": 1, "user_id": 1})},
        json={
            'id': new_assignment_id,
            'teacher_id': 1
        })
    assert submit_response.status_code == 200

    grade_response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": new_assignment_id,
            "grade": GradeEnum.A.value
        }
    )
    assert grade_response.status_code == 200

    regrade_response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_1,
        json={
            "id": new_assignment_id,
            "grade": GradeEnum.B.value
        }
    )
    assert regrade_response.status_code == 400

def test_teacher_view_empty_assignments(client, h_teacher_1):
    # Clear all assignments for this teacher
    Assignment.query.filter_by(teacher_id=1).delete()
    db.session.commit()
    
    response = client.get('/teacher/assignments', headers=h_teacher_1)
    assert response.status_code == 200
    assert len(response.json['data']) == 0

def test_teacher_grade_other_teachers_assignment(client, h_teacher_1, h_teacher_2):
    # First, create a new assignment
    create_response = client.post(
        '/student/assignments',
        headers={'X-Principal': json.dumps({"student_id": 1, "user_id": 1})},
        json={
            'content': 'Test assignment'
        })
    assert create_response.status_code == 200
    new_assignment_id = create_response.json['data']['id']

    # Submit the assignment to teacher 1
    submit_response = client.post(
        '/student/assignments/submit',
        headers={'X-Principal': json.dumps({"student_id": 1, "user_id": 1})},
        json={
            'id': new_assignment_id,
            'teacher_id': 1
        })
    assert submit_response.status_code == 200

    grade_response = client.post(
        '/teacher/assignments/grade',
        headers=h_teacher_2,
        json={
            "id": new_assignment_id,
            "grade": GradeEnum.A.value
        }
    )
    assert grade_response.status_code == 400
    assert 'error' in grade_response.json
    assert 'This assignment belongs to some other teacher' in grade_response.json['message']