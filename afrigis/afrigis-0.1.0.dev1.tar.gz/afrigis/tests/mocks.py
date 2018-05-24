import json

afrigis_geocode_unauthenticated_mock = json.dumps({
    'statusCode': 401,
    'message': 'Invalid Authentication',
    'source': 'SaaS'
}).encode('utf-8')

afrigis_geocode_success_mock = json.dumps({
    'number_of_records': 1,
    'qtime': 83,
    'code': 200,
    'message': 'OK',
    'result': [
        {
            'docid': 'fake-doc-id',
            'seoid': 'fake-seo-id',
            'formatted_address': 'fake-address-string',
            'confidence': 1,
            'address_components': [
                {
                    'type': 'street_number',
                    'administrative_type': 'street_number',
                    'long_name': 'fake-street-number',
                    'short_name': 'fake-street-number'
                },
                {
                    'type': 'route',
                    'administrative_type': 'route',
                    'long_name': 'fake-street-name',
                    'short_name': 'fake-street-name'
                },
                {'type': 'sublocality',
                 'administrative_type': 'suburb',
                 'long_name': 'fake-suburb',
                 'short_name': 'fake-suburb'
                 },
                {
                    'type': 'locality',
                    'administrative_type': 'town',
                    'long_name': 'fake-town',
                    'short_name': 'fake-town'
                },
                {
                    'type': 'administrative_area_level_2',
                    'administrative_type': 'district municipality',
                    'long_name': 'fake-district',
                    'short_name': 'fake-district'
                },
                {
                    'type': 'administrative_area_level_1',
                    'administrative_type': 'province',
                    'long_name': 'fake-province',
                    'short_name': 'fake-province'
                },
                {
                    'type': 'country',
                    'administrative_type': 'country',
                    'long_name': 'fake-country',
                    'short_name': 'fake-country'
                },
                {
                    'type': 'postal_code',
                    'administrative_type': 'post_box',
                    'long_name': 'fake-postal-code',
                    'short_name': 'fake-postal-code'
                },
                {
                    'type': 'postal_code',
                    'administrative_type': 'post_street',
                    'long_name': 'fake-street-postal-code',
                    'short_name': 'fake-street-postal-code'
                }
            ],
            'geometry': {
                'location': {
                    'lat': 1.11,
                    'lng': 2.33
                }
            },
            'types': ['street_address']
        },
    ],
    'source': 'intiendols.geocode.3'
}).encode('utf-8')
