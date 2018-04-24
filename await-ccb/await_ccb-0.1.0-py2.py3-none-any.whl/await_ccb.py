"""Await CCB.

Awaits a successful Google Cloud Container Builder job for a given git repo SHA

Usage:
    await-ccb -c credentials.json -r repo-name -s git-sha [-t -p my-project]
    await-ccb --help
    await-ccb --version

Options:
    -c CREDENTIALS_JSON, --credentials CREDENTIALS_JSON
        Path to service account credentials in Google JSON format.
    -p PROJECT, --project PROJECT
        Google Code Project ID, defaults to project from credentials

Wait for a build of a specific git SHA:
    -r REPO, --repo REPO  Repo name, as known to CCB
    -s SHA, --sha SHA     Git SHA to await
    -t, --trigger         Trigger a build if one is not found

"""
from docopt import docopt
from google.oauth2 import service_account
from time import sleep
from sys import exit
import googleapiclient.discovery

if __name__ == '__main__':
    arguments = docopt(__doc__, version='await-ccb 0.1.0')

    poller = BuildPoller(
        credentials_path=arguments['--credentials'],
        project=arguments['--project'],
        repo=arguments['--repo'],
        sha=arguments['--sha'],
        trigger=arguments['--trigger']
    )

    if poller.await_success():
        exit(0)
    else:
        exit(1)
