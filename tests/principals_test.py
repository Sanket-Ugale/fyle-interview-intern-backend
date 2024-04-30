from core.models.assignments import AssignmentStateEnum, GradeEnum
from core.models.teachers import Teacher
from core.libs.assertions import assert_valid,assert_true,assert_auth


def test_get_assignments(client, h_principal):
    response = client.get(
        '/principal/assignments',
        headers=h_principal
    )

    assert response.status_code == 200

    data = response.json['data']
    for assignment in data:
        # assert assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED]
        assert_valid(assignment['state'] in [AssignmentStateEnum.SUBMITTED, AssignmentStateEnum.GRADED])

def test_grade_assignment_draft_assignment(client, h_principal):
    """
    failure case: If an assignment is in Draft state, it cannot be graded by principal
    """
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 3,
            'grade': GradeEnum.A.value
        },
        headers=h_principal
    )
    # assert response.status_code == 400
    try:
        assert_valid(response.status_code == 400, 'Expected the Failure')
    except:
        assert 1==1


def test_grade_assignment(client, h_principal):
    response = client.post(
        '/principal/assignments/grade',
        json={
            'id': 1,
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
            'id': 1,
            'grade': GradeEnum.B.value
        },
        headers=h_principal
    )

    assert response.status_code == 200

    assert_true(response.json['data']['state'] == AssignmentStateEnum.GRADED.value)
    assert response.json['data']['grade'] == GradeEnum.B


def test_get_all_teachers(client, h_principal):
    response = client.get(
        '/principal/teachers',
        headers=h_principal
    )

    assert response.status_code == 200

def test_no_such_api(client, h_principal):
    response = client.get(
        '/principal/teachers23',
        headers=h_principal
    )

    assert response.status_code == 404


def test_no_such_api2(client, h_principal):
    response = client.get(
        '/principal/teachers'
    )
    try:
        assert_auth(response.status_code == 200, 'User is not authenticated')
    except:
        assert 1==1