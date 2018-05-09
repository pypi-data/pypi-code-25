import os
import click
from subprocess import Popen, PIPE


class lsBranch(object):
    """Main package class"""

    def __init__(self, path='.'):
        self._path = path
        self._git_dirs = []
        self._count_dirs = 0
        self.terminal_size = click.get_terminal_size()[0]

    def search(self, recursive=False):
        """Main function. Scaning through folders on disk."""

        def search_dir(path, recursive):
            for dirname, dirnames, filenames in os.walk(path):

                for subdirname in dirnames:
                    git_dir = os.path.join(dirname, subdirname, '.git')
                    full_path = click.format_filename(os.path.abspath(
                        os.path.join(dirname, subdirname)))

                    self._count_dirs += 1

                    if os.path.exists(git_dir):
                        branch = self._git_branch(git_dir)

                        if not branch:
                            continue

                        self._echo_branch(full_path, branch)

                        self._save(full_path, branch)
                    else:
                        self._echo_dir(full_path)

                        if recursive and subdirname[0] != '.':
                            search_dir(os.path.join(dirname, subdirname),
                                       recursive)
                break

        # start search
        search_dir(self._path, recursive)

        # erase last line of the search
        click.echo(' '*self.terminal_size)

    def _git_branch(self, git_dir):
        """Find out what is current branch in full_path"""

        process = Popen(['git', '--git-dir=' + git_dir, 'branch'],
                        stdout=PIPE, stderr=PIPE)
        stdout, stderr = process.communicate()
        return stdout.decode('utf-8').replace('\n', '') \
            .split('* ')[-1].split(' ')[0]

    def _echo_branch(self, full_path, branch):
        """Print the path and branch in terminal"""

        click.echo(full_path, nl=False)
        click.secho(' ' + '.'*(self.terminal_size-len(full_path)-len(branch)-3) + ' ',
                    nl=False, fg='white', dim=True)
        click.secho(branch, fg='green')

    def _echo_dir(self, full_path):
        """Print path with no git in terminal"""

        if len(full_path) >= self.terminal_size:
            full_path = full_path[:int(self.terminal_size/2)-5] + ' ... ' + \
                full_path[-(int(self.terminal_size/2)-5):]
        click.secho(full_path + '\r', nl=False, fg='blue')

    def _save(self, path, branch):
        """Save git dir in memory"""

        self._git_dirs.append({
            'path': path,
            'branch': branch
        })

    def counter_all(self):
        """All searched dirs counter"""

        return self._count_dirs

    def counter_git(self):
        """Git dirs counter"""

        return len(self._git_dirs)
