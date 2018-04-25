try:
    from urllib2 import Request
    from urllib2 import urlopen
    from urllib2 import HTTPError
except ImportError:
    from urllib.request import Request
    from urllib.request import urlopen
    from urllib.error import HTTPError
import json
from tambo import Transport
from github_status import util, conf


class Create(object):

    _help = """
Create a status for a given commit (sha).
    """

    def __init__(self, argv=None):
        self.argv = argv

    def help(self):
        return self._help

    def update(self):
        state = conf['env']['GITHUB_STATUS_STATE']
        target_url = conf['env'].get('PARENT_BUILD_URL') or conf['env']['BUILD_URL']
        context = conf['env']['GITHUB_STATUS_CONTEXT']
        description_state = dict(
            success=conf['env']['GITHUB_STATUS_SUCCESS'],
            failure=conf['env']['GITHUB_STATUS_FAILURE'],
            error=conf['env']['GITHUB_STATUS_ERROR'],
            pending=conf['env']['GITHUB_STATUS_STARTED']
        )
        url = util.construct_url()
        description = description_state[state]
        data = json.dumps(dict(
            state=state,
            target_url=target_url,
            description=description,
            context=context
        ))
        headers = dict(
            Authorization='token %s' % conf['env']['GITHUB_OAUTH_TOKEN']
        )
        headers['Content-Type'] = 'application/json'
        headers['Content-Length'] = len(data)

        req = Request(url, data, headers)
        try:
            f = urlopen(req)
        except HTTPError as error:
            print('Unable to set the status for %s' % url)
            print(error.read())
            return
        response = f.read()
        print(json.loads(response))
        f.close()

    def main(self):
        parser = Transport(self.argv, check_help=False)
        parser.catch_help = self.help()
        parser.catches_help()
        if util.build_is_triggered():
            print('Build has been triggered via Github, will skip setting status')
            return
        print('Build has not been triggered via Github')
        print('Assuming manual job execution, will set status')

        required_env_vars = [
            'GITHUB_REPOSITORY',
            'GITHUB_SHA',
            'GITHUB_OAUTH_TOKEN',
            'GITHUB_STATUS_CONTEXT',
            'GITHUB_STATUS_STARTED',
            'GITHUB_STATUS_SUCCESS',
            'GITHUB_STATUS_FAILURE',
            'GITHUB_STATUS_ERROR',
            'GITHUB_STATUS_STATE',
            'BUILD_URL']
        missing_envs = []
        for env in required_env_vars:
            if not conf['env'].get(env):
                missing_envs.append(env)

        if missing_envs:
            print('Will skip setting status')
            print('Environment variable(s) required but not provided:')
            for env in missing_envs:
                print('\t ' + env)
            return

        self.update()
