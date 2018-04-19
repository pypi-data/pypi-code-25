from contextlib import suppress

from clusterone import ClusteroneClient
from .actions import register_user, login, init_project_from_github, start_job, create_job, set_endpoint, logout, \
    check_outputs
from .scenario import Scenario
from .types import Output
from .utilities import generate_random_credentials, authorize_client_via_session_file, poll


class GettingStarted(Scenario):
    """
    Mimicking programmatically our onboarding tutorial
    """

    def __init__(self):
        self.url = "https://clusterone.com/api/"
        self.job_name = "clusterone-test-bob"
        self.project_name = "clusterone-test-mnist"
        self.testing_credentials = generate_random_credentials()
        self.any_output_timeout = 600  # seconds
        self.checkpoint_output_timeout = 300  # seconds
        self.loss_output_timeout = 300  # seconds
        self.poll_interval = 10  # seconds

        self.client = ClusteroneClient(username=self.testing_credentials.username, api_url=self.url)

        logout()
        set_endpoint(self.url)

    def run(self):
        register_user(self.testing_credentials, client=self.client)
        login(self.testing_credentials)

        # This is a hax
        authorize_client_via_session_file(client=self.client)

        init_project_from_github(name=self.project_name)

        create_job(self.project_name, self.job_name, module="mnist")
        start_job(self.project_name, self.job_name)

        check_outputs(Output.NONE, client=self.client)

        # TODO: Test for events to know when the pods have started
        # TODO: After that reduce the timeout on any outputs

        poll(check_outputs, args=(Output.ANY,), kwargs={"client": self.client}, timeout=self.any_output_timeout,
            interval=self.poll_interval)

        poll(check_outputs, args=(Output.TENSORFLOW,), kwargs={"client": self.client},
             timeout=self.checkpoint_output_timeout,
             interval=self.poll_interval)

        poll(check_outputs, args=(Output.LOSS,), kwargs={"client": self.client},
             timeout=self.checkpoint_output_timeout,
             interval=self.poll_interval)

    def clean(self):
        # TODO: Do this better
        from .utilities import just_exec, call

        with suppress(AssertionError):
            # TODO: move this to actions
            just_exec("stop -p {}/{}".format(self.project_name, self.job_name))

        # TODO: move this to actions
        call("rm -rf mnist", asserted=False)
