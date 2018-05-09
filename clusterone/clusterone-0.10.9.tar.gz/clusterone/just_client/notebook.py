class Notebook(object):
    """
    Handle of jupyter notebook
    """

    def _initialize(self, api_response):
        """
        This works as __init__

        For production code make sure that the passed data is real, up to date response from Clusterone API
        Also: might be useful for testing.
        """

        self.url = api_response['notebook_url']
        self.id = api_response['job_id']

    def __init__(self, client, configuration):
        """
        Create a brand new notebook and return a handle

        The method is overwritten to have nice API, see _initialize for initialisation
        """

        response = client.client_action(['notebooks', 'create'], params={
            'repository': configuration['code'],
            'display_name': configuration['name'],
            'description': configuration['description'],
            'parameters': configuration,
            'datasets_set': configuration['datasets_set'],
            'git_commit_hash': configuration['code_commit']
        }, validate=True)

        self._initialize(response)

    @classmethod
    def from_clusterone(cls, client, path_or_uuid):
        """
        Obtains the handle of existing jupyter notebook from Clusterone.
        """

        raise NotImplementedError()

        # TODO: Implement this
        response = ""

        # to avoid triggering __init__
        bare_instance = cls.__new__(cls)
        bare_instance._initialize(response)
        return bare_instance

    def __eq__(self, other):
        return self.id == other.id
