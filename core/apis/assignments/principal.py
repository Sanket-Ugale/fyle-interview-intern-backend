from flask import Blueprint
from core import db
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from core.models.teachers import Teacher
from flask import Response, jsonify, make_response


from .schema import AssignmentSchema, AssignmentSubmitSchema, TeacherSchema, AssignmentGradeSchema
principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)


@principal_assignments_resources.route("/assignments",methods=['GET'], strict_slashes=False,)
@decorators.authenticate_principal
def list_assignments(p):
    """Returns list of all submitted and graded assignments"""
    all_assignments = Assignment.get_all_submitted_graded_assignments()
    all_assignments_dump = AssignmentSchema().dump(all_assignments, many=True)
    return APIResponse.respond(data=all_assignments_dump)


@principal_assignments_resources.route("/teachers",methods=['GET'], strict_slashes=False,)
@decorators.authenticate_principal
def list_all_the_teachers(p):
    """ Returns list of all teachers """
    all_teachers = Teacher.get_all_teachers()
    all_teachers_dump = TeacherSchema().dump(all_teachers, many=True)
    return APIResponse.respond(data = all_teachers_dump)



@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_assignment(p, incoming_payload):
    """Grade or re-grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)
    # Check if the assignment is in Draft state
    assignment = Assignment.get_by_id(grade_assignment_payload.id)
    if assignment.state == AssignmentStateEnum.DRAFT:
        return make_response(jsonify(data="Draft assignments cannot be graded by a principal"), 400)
        # return APIResponse.respond(data="Draft assignments cannot be graded by a principal")

    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )

    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    return APIResponse.respond(data=graded_assignment_dump)