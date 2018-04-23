from directory_cms_client.base import BaseAPIClient


class FindASupplierClient(BaseAPIClient):

    page_types = {
        'industries-landing-page': 'find_a_supplier.IndustryLandingPage',
        'landing-page': 'find_a_supplier.LandingPage',
        'industry-contact-page': 'find_a_supplier.IndustryContactPage',
    }

    def get_industries_landing_page(self, *args, **kwargs):
        return self.lookup_by_page_type(
            page_type=self.page_types['industries-landing-page'],
            *args,
            **kwargs
        )

    def get_landing_page(self, *args, **kwargs):
        return self.lookup_by_page_type(
            page_type=self.page_types['landing-page'],
            *args,
            **kwargs
        )

    def get_industry_contact_page(self, *args, **kwargs):
        return self.lookup_by_page_type(
            page_type=self.page_types['industry-contact-page'],
            *args,
            **kwargs
        )
