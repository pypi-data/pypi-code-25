
import json

version_json = '''
{"version": "0.13.0.post2", "dirty": false, "full-revisionid": "3499209b3d7e3416ba28a624f06afac63522ff3d", "error": null, "date": "2018-05-21T13:04:31.346206"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

