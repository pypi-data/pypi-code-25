'''
Preprocessor for Foliant documentation authoring tool.
Allows to run arbitrary external commands.
'''

import re
from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'commands': [],
        'targets': [],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.logger = self.logger.getChild('runcommands')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def apply(self):
        self.logger.info('Applying preprocessor')

        self.logger.debug(f'Allowed targets: {self.options["targets"]}')
        self.logger.debug(f'Current target: {self.context["target"]}')

        if not self.options['targets'] or self.context['target'] in self.options['targets']:
            if self.options['commands']:
                project_dir_pattern = re.compile(
                    '(\$\{PROJECT_DIR\})'
                )

                src_dir_pattern = re.compile(
                    '(\$\{SRC_DIR\})'
                )

                working_dir_pattern = re.compile(
                    '(\$\{WORKING_DIR\})'
                )

                backend_pattern = re.compile(
                    '(\$\{BACKEND\})'
                )

                target_pattern = re.compile(
                    '(\$\{TARGET\})'
                )

                for command in self.options['commands']:
                    command = re.sub(
                        project_dir_pattern,
                        f'{self.project_path.absolute().as_posix()}',
                        command
                    )

                    command = re.sub(
                        src_dir_pattern,
                        f'{(self.project_path / self.config["src_dir"]).absolute().as_posix()}',
                        command
                    )

                    command = re.sub(
                        working_dir_pattern,
                        f'{self.working_dir.absolute().as_posix()}',
                        command
                    )

                    command = re.sub(
                        backend_pattern,
                        f'{self.context["backend"]}',
                        command
                    )

                    command = re.sub(
                        target_pattern,
                        f'{self.context["target"]}',
                        command
                    )

                    try:
                        self.logger.debug(f'Running command: {command}')

                        run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

                    except CalledProcessError as exception:
                        self.logger.error(str(exception))

                        raise RuntimeError(f'Failed: {exception.output.decode()}')

        self.logger.info('Preprocessor applied')
