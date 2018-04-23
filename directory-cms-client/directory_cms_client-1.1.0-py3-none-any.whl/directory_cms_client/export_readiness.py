from directory_cms_client.base import BaseAPIClient


class ExportReadinessClient(BaseAPIClient):

    page_types = {
        'terms-and-conditions': 'export_readiness.TermsAndConditionsPage',
        'privacy-and-cookies': 'export_readiness.PrivacyAndCookiesPage',
    }

    def get_terms_and_conditions_page(self, *args, **kwargs):
        return self.lookup_by_page_type(
            page_type=self.page_types['terms-and-conditions'],
            *args,
            **kwargs
        )

    def get_privacy_and_cookies_page(self, *args, **kwargs):
        return self.lookup_by_page_type(
            page_type=self.page_types['privacy-and-cookies'],
            *args,
            **kwargs
        )
