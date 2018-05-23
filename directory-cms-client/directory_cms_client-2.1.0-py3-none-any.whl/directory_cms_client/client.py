import directory_client_core.base


class DirectoryCMSClient(directory_client_core.base.BaseAPIClient):
    endpoints = {
        'page-by-type': '/api/pages/lookup-by-type/{page_type}/',
        'page-by-slug': '/api/pages/lookup-by-slug/{slug}/',
        'pages-by-type': '/api/pages/'
    }

    def get(self, language_code, draft_token, params=None, *args, **kwargs):
        params = params or {}
        if language_code:
            params['lang'] = language_code
        if draft_token:
            params['draft_token'] = draft_token
        return super().get(params=params, *args, **kwargs)

    def lookup_by_page_type(
        self, page_type, fields=None, draft_token=None, language_code=None
    ):
        return self.get(
            url=self.endpoints['page-by-type'].format(page_type=page_type),
            params={'fields': fields or ['*']},
            draft_token=draft_token,
            language_code=language_code
        )

    def lookup_by_slug(
        self, slug, fields=None, draft_token=None, language_code=None
    ):
        return self.get(
            url=self.endpoints['page-by-slug'].format(slug=slug),
            params={'fields': fields or ['*']},
            draft_token=draft_token,
            language_code=language_code
        )

    def list_by_page_type(
        self, page_type, fields=None, draft_token=None, language_code=None
    ):
        return self.get(
            url=self.endpoints['pages-by-type'],
            params={
                'fields': fields or ['*'],
                'type': page_type,
            },
            draft_token=draft_token,
            language_code=language_code
        )
