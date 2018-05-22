"Library to interact with portainer API"

import logging

import requests


class Portainer(object):
    "Script object to interact with portainer API"
    # pylint: disable=too-many-instance-attributes,too-many-arguments

    def __init__(self, baseurl, username, password):
        """Portainer object constructor

        :param str baseurl: Portainer base url
        :param str username: Username to authenticate
        :param str passworwd: User password
        """
        self.baseurl = baseurl
        self.jwt_token = None
        self.endpoints = None

        self.users = None
        self.teams = None
        self.team_memberships = None

        self.__login(username, password)

    def get_all_data(self):
        "Get all portainer data"
        self.get_endpoints()
        self.get_teams()
        self.get_users()
        self.get_team_memberships()

    def __login(self, username, password):
        """Get JWT token from portainer Auth

        :param str username: Username to authenticate
        :param str passworwd: User password

        :return bool: If the authentication was successful.
        """
        response = requests.post(
            "%s/api/auth" % self.baseurl,
            json={'Username': username, 'Password': password})
        if response.status_code == 200:
            logging.info("Portainer Login succeeded!")
            self.jwt_token = response.json()['jwt']
            return True

        logging.error("Portainer login failed!")
        logging.debug(response.__dict__)
        logging.debug(response.request.__dict__)
        logging.debug(response.history[0].__dict__)
        return False

    def get_endpoints(self):
        """Get all endpoints from portainer API

        :return list: List with endpoints
        :see https://app.swaggerhub.com/apis/deviantony/Portainer/1.15.5/
        """
        logging.info("Get portainer endpoints...")
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        response = requests.get(
            "%s/api/endpoints" % self.baseurl,
            headers=headers)
        if response.status_code == 200:
            self.endpoints = response.json()
            logging.info("Get %d endpoints from portainer",
                         len(self.endpoints))
            return self.endpoints

        logging.error("Can't get endpoints, status %d",
                      response.status_code)
        logging.debug(response.__dict__)
        return None

    def get_teams(self):
        """Get all teams from portainer API

        :return list: List with teams
        :see https://app.swaggerhub.com/apis/deviantony/Portainer/1.15.5/
        """
        logging.info("Get portainer teams...")
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        response = requests.get(
            "%s/api/teams" % self.baseurl,
            headers=headers)
        if response.status_code == 200:
            self.teams = response.json()
            logging.info("Get %d teams from portainer",
                         len(self.teams))
            return self.teams

        logging.error("Can't get teams, status %d",
                      response.status_code)
        logging.debug(response.__dict__)
        return None

    def get_users(self):
        """Get all users from portainer API

        :return list: List with users
        :see https://app.swaggerhub.com/apis/deviantony/Portainer/1.15.5/
        """
        logging.info("Get portainer users...")
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        response = requests.get(
            "%s/api/users" % self.baseurl,
            headers=headers)
        if response.status_code == 200:
            self.users = response.json()
            logging.info("Get %d users from portainer",
                         len(self.users))
            return self.teams

        logging.error("Can't get users, status %d",
                      response.status_code)
        logging.debug(response.__dict__)
        return None

    def get_team_memberships(self):
        """Get all team memberships from portainer API

        :return list: List with team memberships
        :see https://app.swaggerhub.com/apis/deviantony/Portainer/1.15.5/
        """
        logging.info("Get portainer team memberships...")
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        response = requests.get(
            "%s/api/team_memberships" % self.baseurl,
            headers=headers)
        if response.status_code == 200:
            self.team_memberships = response.json()
            logging.info("Get %d team memberships from portainer",
                         len(self.team_memberships))
            return self.team_memberships

        logging.error("Can't get team memberships, status %d",
                      response.status_code)
        logging.debug(response.__dict__)
        return None

    def create_endpoint(self, name, url, tls=True):
        """Create endpoint in portainer

        :param str name: Endpoint name
        :param str url: Endpoint URL
        :param str tls: If endpoint use TLS. Default: True

        :return dict: Portainer API Response
        :see https://app.swaggerhub.com/apis/deviantony/Portainer/1.15.5/
        """
        logging.info("Creating portainer endpoint %s...", name)
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        payload = {
            'Name': name,
            'URL': url,
            'TLS': tls
        }
        response = requests.post(
            "%s/api/endpoints" % self.baseurl,
            headers=headers,
            json=payload)
        if response.status_code == 200:
            response_json = response.json()
            # self.endpoints.append(
            #     {
            #         'Id': response_json['Id'],
            #         'Name': name
            #     }
            # )
            logging.info(
                "Endpoint %s created in portainer with id %d",
                name, response_json['Id'])
            # TODO: Add full data endpoint to cache
            return response_json

        logging.error("Can't create endpoint %s, status %d",
                      name,
                      response.status_code)
        logging.debug(response.__dict__)
        return None

    def create_team(self, name):
        """Create team in portainer

        :param str name: Team name

        :return dict: Portainer API Response
        :see https://app.swaggerhub.com/apis/deviantony/Portainer/1.15.5/
        """
        logging.info("Creating portainer team %s...", name)
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        payload = {
            'Name': name
        }
        response = requests.post(
            "%s/api/teams" % self.baseurl,
            headers=headers,
            json=payload)
        if response.status_code == 200:
            response_json = response.json()
            self.teams.append(
                {
                    'Id': response_json['Id'],
                    'Name': name
                }
            )
            logging.info("Teams %s created in portainer with id %d",
                         name, response_json['Id'])
            return response_json

        logging.error("Can't create team %s, status %d",
                      name,
                      response.status_code)
        logging.debug(response.__dict__)
        return None

    def create_user(self, username, is_admin=False):
        """Create user in portainer

        :param str username: User login
        :param str is_admin: If user is admin

        :return dict: Portainer API Response
        :see https://app.swaggerhub.com/apis/deviantony/Portainer/1.15.5/
        """
        logging.info("Creating portainer user %s...", username)
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        payload = {
            'username': username,
            'password': '',
            'role': {True: 1}.get(is_admin, 2)
        }
        response = requests.post(
            "%s/api/users" % self.baseurl,
            headers=headers,
            json=payload)
        if response.status_code == 200:
            response_json = response.json()
            self.users.append(
                {
                    'Id': response_json['Id'],
                    'Role': {True: 1}.get(is_admin, 2),
                    'Username': username
                }
            )
            logging.info("User %s created in portainer with id %d",
                         username, response_json['Id'])
            return response_json

        logging.error("Can't create user %s, status %d",
                      username,
                      response.status_code)
        logging.debug(response.__dict__)
        return None

    def create_team_memberships(self, user_id, team_id, role_id):
        """Create user in portainer

        :param int user_id: Portainer user ID
        :param int team_id: Portainer team ID
        :param int role_id: Portainer role ID

        :return dict: Portainer API Response
        :see https://app.swaggerhub.com/apis/deviantony/Portainer/1.15.5/
        """
        logging.info(
            "Creating portainer team membership userid %d to teamid %d "
            "with roleid %d",
            user_id, team_id, role_id
        )
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        payload = {
            'Role': role_id,
            'TeamID': team_id,
            'UserID': user_id
        }
        response = requests.post(
            "%s/api/team_memberships" % self.baseurl,
            headers=headers,
            json=payload)
        if response.status_code == 200:
            response_json = response.json()
            self.team_memberships.append(
                {
                    'Id': response_json['Id'],
                    'Role': role_id,
                    'TeamID': team_id,
                    'UserID': user_id
                }
            )
            logging.info(
                "Team membership userid %d to teamid %d "
                "with roleid %d created with id %d",
                user_id, team_id, role_id, response_json['Id'])
            return response_json

        logging.error("Can't create team membership, status %d",
                      response.status_code)
        logging.debug(response.__dict__)
        return None

    def upload_tls(self, endpoint_id, certificate, upload_file):
        """Add TLS files to endpoint

        :param int endpoint_id: Endpoint id to add TLS files
        :param str certificate: TLS file type.
                                Valid values are 'ca', 'cert' or 'key'.
        :param str upload_file: Path to file to upload.

        :return bool: True if files was upload successful.
        """
        logging.debug("Add TLS files %s to endpoint %d",
                      certificate, endpoint_id)
        # for name, upload_file in {
        #         'ca': open(self.cacert.name, 'rb'),
        #         'cert': open(self.cert.name, 'rb'),
        #         'key': open(self.key.name, 'rb')}.items():
        url = "%s/api/upload/tls/%s?folder=%s" % (
            self.baseurl, certificate, endpoint_id)
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        payload = {'file': open(upload_file, 'rb')}
        response = requests.post(url, files=payload, headers=headers)
        if response.status_code != 200:
            logging.error("Fail to load %s on %s. Status: %d",
                          certificate, endpoint_id,
                          response.status_code)
            logging.debug(response.__dict__)
            return False
        return True

    def endpoint_access(self, endpoint_id, users, teams):
        """Manage user and team accesses to an endpoint.

        :param int endpoint_id: Endpoint identifier.
        :param list users: List with users IDs.
        :param list teams: List with teams IDs.

        :return bool: True if access was success.
        """
        logging.debug("Set access to endpoint %d", endpoint_id)

        url = "%s/api/endpoints/%d/access" % (self.baseurl, endpoint_id)
        headers = {'Authorization': 'Bearer %s' % self.jwt_token}
        payload = {
            'AuthorizedUsers': users,
            'AuthorizedTeams': teams
        }
        response = requests.put(url, json=payload, headers=headers)

        if response.status_code == 200:
            logging.info("Endpoint access set successfuly.")
            return True
        elif response.status_code in (400, 404, 500):
            logging.debug(response.__dict__)
            response_json = response.json()
            logging.error("Fail to set endpoint access on %d: %s. Status: %d",
                          endpoint_id, response_json['err'],
                          response.status_code)
            logging.debug(response.__dict__)
            return False

        logging.error("Fail to set endpoint access on %d: Status: %d",
                      endpoint_id, response.status_code)
        logging.debug(response.__dict__)
        return False
