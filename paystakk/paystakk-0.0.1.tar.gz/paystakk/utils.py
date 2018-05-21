import requests


def validate_post(res):
    if res.status_code == requests.codes.created:
        return res.json()
    else:
        res.raise_for_status()


def validate_get(res):
    if res.status_code == requests.codes.ok:
        return res.json()
    else:
        res.raise_for_status()


def build_params(**kwargs):
    params = {}
    for kw in kwargs:
        if kwargs[kw]:
            if kw.lower() == 'amount':
                params[kw] = kwargs[kw] * 100
            else:
                params[kw] = kwargs[kw]

    return params
