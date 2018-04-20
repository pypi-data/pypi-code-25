import re
import subprocess  # noqa: S404

import github_release


def format_changelog(data):
    lines = data['history_last_release'].splitlines()
    last_line = data['history_insert_line_here']
    lines = ['## Changelog'] + lines[2:last_line]
    return '\n'.join(lines)


def get_github_repository():
    remotes = subprocess.check_output(['git', 'remote', '-v']).decode()  # noqa:S603,S607
    repositories = set(re.findall('git@github.com:(\w+/\w+).git', remotes))
    return repositories.pop()


def ask_direct_question(question, default=None):
    final_marks = {True: '(Y/n)?', False: '(y/N)?', None: '(y/n)?'}
    input_values = {True: ['y', 'yes'], False: ['n', 'no']}
    values = {
        text: value
        for value, inputs in input_values.items()
        for text in inputs
    }

    values[''] = default
    message = '{} {} '.format(
        question.rstrip('?'),
        final_marks[default],
    )

    response = None
    while not isinstance(response, bool):
        raw = input(message)
        response = values.get(raw.lower())
    return response


def publish_release_on_github(data):
    release_tag = data['headings'][0]['version']  # Should be data['version']...
    changelog = format_changelog(data)
    repository = get_github_repository()

    response = ask_direct_question(
        "\n\n{changelog}\n\nPublish release {release} to Github ({repo})?".format(
            changelog=changelog,
            release=release_tag,
            repo=repository,
        ),
        default=True,
    )

    if response:
        try:
            github_release.gh_release_create(
                repository,
                release_tag,
                body=changelog,
                publish=True,
            )
        except EnvironmentError as e:
            print(e)
            print('=> You should create the release manualy.')
