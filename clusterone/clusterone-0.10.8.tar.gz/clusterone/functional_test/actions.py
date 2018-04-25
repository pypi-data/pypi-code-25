"""
Building blocks of a functional tests

Contains high level action as understood by the business.
"""

import subprocess
import logging

from .utilities import just_exec, call, poll
from .types import Output
from coreapi.exceptions import ErrorMessage


def set_endpoint(url):
    just_exec("config endpoint {}".format(url))

    logging.info("using endpoint {}".format(url))


def register_user(user_credentials, client):

    response = client.client_action(['register', 'create'], params={
        'username': user_credentials.username,
        'email': user_credentials.email,
        'password': user_credentials.password,
    }, validate=True)

    assert response['username'] == user_credentials.username
    assert response['email'] == user_credentials.email

    logging.info("registration complete")


def login(user_credentials):

    output = just_exec(
        "login --username {} --password {}".format(user_credentials.username, user_credentials.password))

    assert "successful" in output

    logging.info("login completed")


def logout():
    just_exec("logout")

    logging.debug("credentials clear")


def init_project_from_github(name):
    call("git clone -q https://github.com/clusterone/mnist")
    project_initialization_output = just_exec("init project {} -r ./mnist".format(name))
    subprocess.call("cd mnist; git push -q clusterone", shell=True)

    assert project_initialization_output.split('\n')[1].endswith('clusterone-test-mnist.git')

    logging.info("local and remote project clone completed")

    # check if commits appeared
    poll(just_exec, args=tuple(["create job single --project {} --name {}".format(name, "test_project_has_commits")]), timeout=60, interval=10)


def create_job(project_name, job_name, module="main"):

    job_state = just_exec("get jobs")
    assert job_name not in job_state

    just_exec("create job distributed --name {} --project {} --module {} --time-limit 1h".format(job_name, project_name, module))

    job_state = just_exec("get jobs")
    assert job_name in job_state

    logging.info("job successfully created")


def start_job(project_name, job_name):
    just_exec("start job -p {}/{}".format(project_name, job_name))
    job_status = just_exec("get job {}/{}".format(project_name, job_name))

    assert "started" in job_status

    logging.info("job successfully started")


def check_outputs(desired_outputs, client=None):

    def download_file(filename):
        response = client.client_action(['jobs', 'file', 'read'], params={
            'job_id': job_id,
            'filename': filename
        }, validate=True)

        return response

    job_data = just_exec("get jobs")
    job_data_parsed = job_data.split()
    job_id = job_data_parsed[job_data_parsed.index("None/clusterone-test-bob") + 2]

    try:
        response = client.client_action(['jobs', 'files', 'list'], params={
            'job_id': job_id,
        }, validate=True)
    except ErrorMessage as exception:

        if "404 Not Found" in str(exception.error):
            outputs = []
        else:
            raise
    else:
        outputs = response[0]['contents']

    if desired_outputs == Output.ANY:
        assert outputs
    elif desired_outputs == Output.NONE:
        assert outputs == []
    elif desired_outputs == Output.TENSORFLOW:
        assert any({"ckpt" in output_file['name'] for output_file in outputs})
    elif desired_outputs == Output.LOSS:
        for worker_log in {output_file['name'] for output_file in outputs if "worker" in output_file['name'] and output_file['name'].endswith(".txt")}:
            assert "Loss = " in download_file(worker_log)
    else:
        raise ValueError("Desired_outputs parameter must be correct enum value")

    logging.info("outputs match target {}".format(desired_outputs))
