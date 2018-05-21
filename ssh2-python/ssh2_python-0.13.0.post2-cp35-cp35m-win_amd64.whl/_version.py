
import json

version_json = '''
{"date": "2018-05-21T13:11:17.014610", "version": "0.13.0.post2", "dirty": false, "full-revisionid": "3499209b3d7e3416ba28a624f06afac63522ff3d", "error": null}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

