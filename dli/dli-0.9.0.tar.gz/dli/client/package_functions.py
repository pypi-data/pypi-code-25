import logging
from dli.siren import siren_to_entity
from dli.client.exceptions import PackageNotFoundException


logger = logging.getLogger(__name__)


class PackageFunctions(object):
    """
    A mixin providing common package operations
    """
    def get_s3_access_keys_for_package(self, package_id, refresh=False):
        """
        Retrieve S3 access keys for the specified account to access the
        specified package. The retrieved keys and session token will be stored
        in the client context.

        :param package_id: The id of the package
        :param refresh: Optional flag to force refresh the token.

        :return: A dictionary containing the AWS keys, package id and session
                token. For example:


                .. code-block:: python

                    {
                       "accessKeyId": "39D19A440AFE452B9",
                       "packageId": "d0b545dd-83ee-4293-8dc7-5d0607bd6b10",
                       "secretAccessKey": "F426A93CDECE45C9BFF8F4F19DA5CB81",
                       "sessionToken": "C0CC405803F244CA99999"
                    }
        """
        if package_id in self.ctx.s3_keys and not refresh:
            return self.ctx.s3_keys[package_id]

        # otherwise we go and attempt to fetch one from the API
        root = self.ctx.get_root_siren()
        pf = root.package_forms()
        keys = pf.request_access_keys(package_id=package_id)

        val = {
            "accessKeyId": keys.accessKeyId,
            "packageId": keys.packageId,
            "secretAccessKey": keys.secretAccessKey,
            "sessionToken": keys.sessionToken
        }

        # cache the key for future usages
        self.ctx.s3_keys[package_id] = val

        return val

    def get_package(self, package_id):
        """
        Get a package by id.

        :param package_id: The id of the package
        :return: A package instance
        """
        p = self._get_package(package_id)
        if not p:
            logger.warn("No package found with id `%s`", package_id)
            return

        return siren_to_entity(p)

    def get_package_datasets(self, package_id, count=100):
        package = self._get_package(package_id)
        if package is None:
            raise Exception("No package could be found with id %s" % package_id)

        datasets = package.package_datasets(page_size=count).get_entities(rel="dataset")
        return [siren_to_entity(d) for d in datasets]

    def register_package(
        self,
        package_builder
    ):
        """
        
        :params package_builder:
        :returns: a package 
        """
        # get my accounts so that we can use them as a default for all the roles
        # TODO: Fail if we have more than one account?
        if not package_builder.content_creator or not package_builder.publisher or not package_builder.manager:
            accounts = self.get_my_accounts()
            if len(accounts) > 1:
                raise Exception(
                    "Unable to autoselect content_creator, publisher and manager "
                    "account. Due to multiple accounts being attached to this API key."
                    "Your accounts are: %s" % [(a.id, a.name) for a in accounts]
                    )

            default_account = accounts[0].id
            if not package_builder.contentCreator:
                logger.info("Assigning ourselves as contentCreator as no value was provided.")
                package_builder.contentCreator = default_account
            if not package_builder.manager:
                logger.info("Assigning ourselves as manager as no value was provided.")
                package_builder.manager = default_account
            if not package_builder.publisher:
                logger.info("Assigning ourselves as publisher as no value was provided.")
                package_builder.publisher = default_account

        package = package_builder.build()
        pf = self.get_root_siren().package_forms()
        return siren_to_entity(pf.register_package(__json=package))

    def search_packages(self, term):
        """
        Search packages given a particular set of keywords

        :param term: The search term
        :return: A list of package entities
        """
        packages = self.get_root_siren().list_packages(query=term)
        return packages

    def delete_package(self, package_id):
        """
        Delete a package by id. This will delete all underlying datasets for the package as well

        :param package_id: The id of the package to be deleted
        :return:
        """
        package =  self._get_package(package_id)
        if package:
            package.delete_package(package_id=package_id)
        else:
            raise PackageNotFoundException(f'Package with id {package_id} not found')

    def get_my_accounts(self):
        result = self.get_root_siren().list_my_accounts()
        accounts = result.get_entities(rel="")
        return [siren_to_entity(a) for a in accounts]

    #
    # Private functions
    #

    def _get_package(self, package_id):
        return self.get_root_siren().get_package(package_id=package_id)
