from flask import Blueprint, request
from slerp.logger import logging

from service.subject_service import SubjectService

log = logging.getLogger(__name__)

subject_api_blue_print = Blueprint('subject_api_blue_print', __name__)
api = subject_api_blue_print
subject_service = SubjectService()


@api.route('/add_subject', methods=['POST'])
def add_subject():
    """
    {
    "name": "String",
    "tag": "String",
    "school_id": "Long",
    "user_profile_id": "Long",
    "school": "?",
    "user_profile": "?"
    }
    """
    domain = request.get_json()
    return subject_service.add_subject(domain)


@api.route('/add_subject', methods=['POST'])
def add_subject():
    """
    {
    "name": "String",
    "tag": "String",
    "school_id": "Long",
    "user_profile_id": "Long",
    "school": "?",
    "user_profile": "?"
    }
    """
    domain = request.get_json()
    return subject_service.add_subject(domain)


@api.route('/get_subject_by_id', methods=['GET'])
def get_subject_by_id():

    """
    {
        "page": "Long",
        "size": "Long",
        "id": "Long"
    }
    """
    domain = request.args.to_dict()
    return subject_service.get_subject_by_id(domain)