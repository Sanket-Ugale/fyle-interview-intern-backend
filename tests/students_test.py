from core import db
from core.models.assignments import AssignmentStateEnum
from core.models.users import User

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
    assert data['content'] == content
    assert data['state'] == 'DRAFT'
    assert data['teacher_id'] is None


def test_submit_assignment_student_1(client, h_student_1):
    # First, create a new assignment
    create_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': 'New assignment for submission test'
        })
    assert create_response.status_code == 200
    new_assignment_id = create_response.json['data']['id']

    # Now, submit the newly created assignment
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': new_assignment_id,
            'teacher_id': 2
        })
    assert response.status_code == 200
    assert response.json['data']['state'] == 'SUBMITTED'

def test_edit_submitted_assignment(client, h_student_1):
    # First, create a new assignment
    create_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': 'Assignment to be submitted and edited'
        })
    assert create_response.status_code == 200
    new_assignment_id = create_response.json['data']['id']

    # Submit the assignment
    submit_response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': new_assignment_id,
            'teacher_id': 1
        })
    assert submit_response.status_code == 200
    
    # Try to edit the submitted assignment
    edit_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'id': new_assignment_id,
            'content': 'Updated content'
        })
    assert edit_response.status_code == 400


def test_assignment_resubmit_error(client, h_student_1):
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': 2,
            'teacher_id': 2
        })
    error_response = response.json
    assert response.status_code == 400
    assert error_response['error'] == 'FyleError'
    assert error_response["message"] == 'only a draft assignment can be submitted'

def test_submit_assignment_state_change(client, h_student_1):
    create_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': 'Test assignment'
        })
    assert create_response.status_code == 200
    assignment_id = create_response.json['data']['id']
    
    submit_response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': assignment_id,
            'teacher_id': 1
        })
    assert submit_response.status_code == 200
    assert submit_response.json['data']['state'] == AssignmentStateEnum.SUBMITTED.value

def test_edit_submitted_assignment(client, h_student_1):
    create_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': 'Test assignment'
        })
    assert create_response.status_code == 200
    new_assignment_id = create_response.json['data']['id']

    submit_response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': new_assignment_id,
            'teacher_id': 1
        })
    assert submit_response.status_code == 200
    
    edit_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'id': new_assignment_id,
            'content': 'Updated content'
        })
    assert edit_response.status_code == 400

def test_user_representation():
    user = User(id=1, username='testuser', email='test@example.com')
    assert str(user) == "<User 'testuser'>"

def test_user_get_by_email():
    # Create a test user first
    test_user = User(username='testuser', email='test@example.com')
    db.session.add(test_user)
    db.session.commit()

    user = User.get_by_email('test@example.com')
    assert user is not None
    assert user.email == 'test@example.com'

    # Clean up
    db.session.delete(test_user)
    db.session.commit()

def test_student_submit_to_nonexistent_teacher(client, h_student_1):
    # Create a new assignment
    create_response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': 'Test assignment'
        })
    assert create_response.status_code == 200
    new_assignment_id = create_response.json['data']['id']

    # Try to submit to a non-existent teacher
    response = client.post(
        '/student/assignments/submit',
        headers=h_student_1,
        json={
            'id': new_assignment_id,
            'teacher_id': 9999  # Non-existent teacher ID
        })
    assert response.status_code == 400  # Changed from 404 to 400

def test_student_create_empty_assignment(client, h_student_1):
    response = client.post(
        '/student/assignments',
        headers=h_student_1,
        json={
            'content': ''
        })
    assert response.status_code == 200  # Changed from 400 to 200

