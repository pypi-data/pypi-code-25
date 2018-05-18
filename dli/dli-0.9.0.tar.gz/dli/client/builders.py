
class PackageBuilder:
    """
        Helper builder that allows specifiying the metadata
        a new package requires.

        Packages are parent structures that contain metadata relating
        to a collection of Datasets.
    """
    def __init__(
        self,
        name,
        description,
        data_source=None,
        data_access=None,
        visibility=None,
        product=None,
        industry_or_sector=None,
        region=None,
        content_creator=None,
        publisher=None,
        keywords=None,
        manager=None,
        confidentiality_level=None,
        contract_bound=None,
        internal_usage_rights=None,
        internal_usage_notes=None,
        distribution_rights=None,
        distribution_notes=None,
        derived_data_rights=None,
        derived_data_notes=None,
        data_type=None,
        frequency=None,
        data_format=None,
        documentation=None
    ):
        """
        Initialise this instance with default values.
        See description for each argument, and whether they are optional or required.

        :param name: A unique name representing this package.
        :param description: A more in depth description of what this package
                            is for.
        :param data_source: Accepted values are: `Internal` or `External`
        :param data_access: Accepted values are: `Restricted`, `Unrestricted`
                            Defaults to `Restricted`.
        :param visibility:  Accepted values are: `Internal`, `Public`, `Private`
                            Defaults to `Internal`
        :param industry_or_sector: Defaults to `Other`.
        :param region:
        :param content_creator: Account ID for the group
                                that is considered the SME/Creator of the data
                                represented in this package.
                                Defaults to your account if none provided.
        :param publisher: Account ID for the group that is expected to publish
                          datasets for this package.
                          Defaults to your account if none provided.
        :param keywords: A list of keywords that can be used to find this
                         package through the search interface.
        :param manager: Account ID for the group that is expected to maintain
                        this package (i.e. edit) and grant access requests.
                        Defaults to your account if none provided.
        :param confidentiality_level:
        :param contract_bound:
        :param internal_usage_rights:
        :param internal_usage_notes:
        :param distribution_rights:
        :param distribution_notes:
        :param derived_data_rights:
        :param derived_data_notes:
        :param data_type:
        :param frequency:
        :param data_format:
        :param documentation: Documentation about this package
                              in markdown format.
        """
        self.content_creator = content_creator
        self.manager = manager
        self.publisher = publisher

        self.fields = {
            "name": name,
            "description": description,
            "dataSource": data_source,
            "dataAccess": data_access or "Restricted",
            "visibility": visibility or "Internal",
            "product": product,
            "industrySector": industry_or_sector or "Other",
            "region": region,
            "keywords": keywords or [],
            "confidentialityLevel": confidentiality_level,
            "contractBound": contract_bound,
            "internalUsageRights": internal_usage_rights,
            "internalUsageNotes": internal_usage_notes,
            "distributionRights": distribution_rights,
            "distributionNotes": distribution_notes,
            "derivedDataRights": derived_data_rights,
            "derivedDataNotes": derived_data_notes,
            "dataType": data_type,
            "frequency": frequency,
            "dataFormat": data_format,
            "documentation": documentation or ""
        }
        self.storage = None

    def with_data_lake_storage(self, bucket_name):
        self.storage = {
            "dataStorage": "S3",
            "createS3Bucket": True,
            "s3Bucket": bucket_name
        }
        return self

    def with_external_s3_storage(
        self,
        bucket_name,
        aws_access_key,
        aws_secret_access_key
    ):
        self.storage = {
            "dataStorage": "S3",
            "createS3Bucket": False,
            "s3Bucket": bucket_name,
            "awsAccessKeyId": aws_access_key,
            "awsSecretAccessKey": aws_secret_access_key
        }
        return self

    def with_external_storage(self, location):
        self.storage = {
            "dataStorage": "Other",
            "dataLocation": location
        }
        return self

    def build(self):
        # if no storage provided, then by default we set it to `Other`
        if not self.storage:
            self.with_external_storage("Not Specified")

        payload = dict(self.fields)
        payload.update({
            "contentCreator": {"accountId": self.content_creator},
            "publisher": {"accountId": self.publisher},
            "manager": {"accountId": self.manager},
        })
        payload.update(self.storage)

        # clean not set entries
        payload = {k: v for k, v in payload.items() if v is not None}
        return payload
