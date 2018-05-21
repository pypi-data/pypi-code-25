
import json

version_json = '''
{"date": "2018-05-21T12:52:11.116000", "full-revisionid": "3499209b3d7e3416ba28a624f06afac63522ff3d", "dirty": false, "version": "0.13.0.post2", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

