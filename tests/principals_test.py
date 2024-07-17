from core import db
from core.models.assignments import Assignment, AssignmentStateEnum, GradeEnum


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]


def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 5,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )

    assert response.status_code == 400


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.C.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.C


def test_regrade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 4,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value
    assert response.json['data']['grade'] == GradeEnum.B

def test_get_submitted_and_graded_assignments(client, h_principal):
    response = client.get('/principal/assignments', headers=h_principal)
    assert response.status_code == 200
    data = response.json['data']
    for assignment in data:
        assert assignment['state'] in [AssignmentStateEnum.SUBMITTED.value, AssignmentStateEnum.GRADED.value]

def test_get_teachers(client, h_principal):
    response = client.get('/principal/teachers', headers=h_principal)
    assert response.status_code == 200
    data = response.json['data']
    assert len(data) > 0
    for teacher in data:
        assert 'id' in teacher
        assert 'user_id' in teacher

def test_principal_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 1,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )
    assert response.status_code == 200
    data = response.json['data']
    assert data['grade'] == GradeEnum.A.value
    assert data['state'] == AssignmentStateEnum.GRADED.value

def test_principal_regrade_assignment(client, h_principal):
    # First, grade the assignment
    client.post(
        '/principal/assignments/grade',
        json={
            'id': 1,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )
    
    # Then, regrade it
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 1,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )
    assert response.status_code == 200
    data = response.json['data']
    assert data['grade'] == GradeEnum.B.value
    assert data['state'] == AssignmentStateEnum.GRADED.value

def test_principal_grade_draft_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 2,  # Assuming this is a draft assignment
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )
    assert response.status_code == 400

def test_principal_view_assignments_without_authentication(client):
        response = client.get('/principal/assignments')
        assert response.status_code == 401  # Assuming 401 is used for authentication errors

def test_principal_view_teachers_without_authentication(client):
        response = client.get('/principal/teachers')
        assert response.status_code == 401  # Assuming 401 is used for authentication errors

def test_principal_grade_submitted_assignment(client, h_principal):
    # Ensure there's a submitted assignment
    client.post(
        '/student/assignments/submit',
        headers={'X-Principal': '{"user_id": 1, "student_id": 1}'},
        json={
            'id': 2,
            'teacher_id': 1
        })
    
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 2,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )
    assert response.status_code == 200
    assert response.json['data']['grade'] == GradeEnum.B.value
    assert response.json['data']['state'] == AssignmentStateEnum.GRADED.value

def test_principal_regrade_assignment(client, h_principal):
    # First, grade an assignment
    client.post(
        '/principal/assignments/grade',
        json={
            'id': 1,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )
    
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 1,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )
    assert response.status_code == 200
    assert response.json['data']['grade'] == GradeEnum.B.value

def test_principal_list_teachers(client, h_principal):
    response = client.get('/principal/teachers', headers=h_principal)
    assert response.status_code == 200
    assert 'data' in response.json
    assert isinstance(response.json['data'], list)

from core.models.principals import Principal

def test_principal_representation():
    principal = Principal(id=1, user_id=1)
    assert str(principal) == '<Principal 1>'

def test_principal_grade_nonexistent_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 9999,  # Non-existent assignment ID
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )
    assert response.status_code == 404

def test_principal_grade_invalid_grade(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 1,
            'grade': 'INVALID_GRADE'
        },
        headers=h_principal
    )
    assert response.status_code == 400

def test_principal_view_empty_assignments(client, h_principal):
    # Clear all assignments before this test
    Assignment.query.delete()
    db.session.commit()
    
    response = client.get('/principal/assignments', headers=h_principal)
    assert response.status_code == 200
    assert len(response.json['data']) == 0
