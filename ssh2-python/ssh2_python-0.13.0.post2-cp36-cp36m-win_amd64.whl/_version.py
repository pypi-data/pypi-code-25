
import json

version_json = '''
{"date": "2018-05-21T13:24:59.710365", "dirty": false, "error": null, "full-revisionid": "3499209b3d7e3416ba28a624f06afac63522ff3d", "version": "0.13.0.post2"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

