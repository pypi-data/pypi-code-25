'''
Preprocessor for Foliant documentation authoring tool.
Converts EPS images to PNG format.
'''

import re

from pathlib import Path
from hashlib import md5
from subprocess import run, PIPE, STDOUT, CalledProcessError

from foliant.preprocessors.base import BasePreprocessor


class Preprocessor(BasePreprocessor):
    defaults = {
        'convert_path': 'convert',
        'cache_dir': Path('.epsconvertcache'),
        'image_width': 0,
        'targets': [],
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._source_img_ref_pattern = re.compile("!\[(?P<caption>.*)\]\((?P<path>((?!:\/\/).)+\/[^\/]+\.eps)\)")
        self._cache_path = self.project_path / self.options['cache_dir']
        self._current_dir = self.working_dir

        self.logger = self.logger.getChild('epsconvert')

        self.logger.debug(f'Preprocessor inited: {self.__dict__}')

    def _process_epsconvert(self, img_caption: str, img_path: str) -> str:
        source_img_path = self._current_dir / img_path

        self.logger.debug(f'Source image path: {source_img_path}')

        img_hash = md5(f'{self.options["image_width"]}'.encode())

        with open(source_img_path.absolute().as_posix(), 'rb') as source_img_file:
            source_img_file_body = source_img_file.read()
            img_hash.update(f'{source_img_file_body}'.encode())

        cached_img_path = self._cache_path / f'{img_hash.hexdigest()}.png'
        cached_img_ref = f'![{img_caption}]({cached_img_path.absolute().as_posix()})'

        self.logger.debug(f'Cached image path: {cached_img_path}')

        if cached_img_path.exists():
            self.logger.debug(f'Cached image already exists')

            return cached_img_ref

        cached_img_path.parent.mkdir(parents=True, exist_ok=True)

        resize_options = ''

        if self.options["image_width"] > 0:
            resize_options = f'-resize {self.options["image_width"]}'

        try:
            command = f'{self.options["convert_path"]} ' \
                      f'{source_img_path.absolute().as_posix()} ' \
                      f'-format png ' \
                      f'{resize_options} ' \
                      f'{cached_img_path.absolute().as_posix()}'

            run(command, shell=True, check=True, stdout=PIPE, stderr=STDOUT)

            self.logger.debug(f'Cached image saved, width: {self.options["image_width"]} (0 means auto)')

        except CalledProcessError as exception:
            self.logger.error(str(exception))

            raise RuntimeError(
                f'Processing of image {img_path} failed: {exception.output.decode()}'
            )

        return cached_img_ref

    def process_epsconvert(self, content: str) -> str:
        def _sub(source_img_ref) -> str:
            return self._process_epsconvert(
                source_img_ref.group('caption'),
                source_img_ref.group('path')
            )

        return self._source_img_ref_pattern.sub(_sub, content)

    def apply(self):
        self.logger.info('Applying preprocessor')

        self.logger.debug(f'Allowed targets: {self.options["targets"]}')
        self.logger.debug(f'Current target: {self.context["target"]}')

        if not self.options['targets'] or self.context['target'] in self.options['targets']:
            for markdown_file_path in self.working_dir.rglob('*.md'):
                with open(markdown_file_path, encoding='utf8') as markdown_file:
                    content = markdown_file.read()

                with open(markdown_file_path, 'w', encoding='utf8') as markdown_file:
                    self._current_dir = markdown_file_path.parent
                    markdown_file.write(self.process_epsconvert(content))

        self.logger.info('Preprocessor applied')
