import asyncio
import json
import logging
import os
import re
import shutil
import subprocess
from functools import partial
from time import time

from grablib.build import SassGenerator, insert_hash
from grablib.common import GrablibError
from grablib.download import Downloader
from pygments.formatters.html import HtmlFormatter

from .common import HarrierProblem, log_complete
from .config import Config, Mode

logger = logging.getLogger('harrier.assets')


def run_grablib(config: Config):
    start = time()
    download_root = config.theme_dir / 'libs'
    log_msg = False
    if config.download:
        logger.debug('running grablib download...')
        download = Downloader(
            download_root=download_root,
            download=config.download,
            aliases=config.download_aliases,
            lock=config.theme_dir / '.grablib.lock',
        )
        download()
        log_msg = True

    sass_dir = config.theme_dir / 'sass'
    count = 0
    if sass_dir.is_dir():
        output_dir = config.dist_dir / config.dist_dir_sass
        output_dir.relative_to(config.dist_dir)

        # this prevents SassGenerator from throwing an error because this directory exists
        out_dir_src = output_dir / '.src'
        out_dir_src.is_dir() and shutil.rmtree(out_dir_src)

        theme_files = find_theme_files(config)
        custom_functions = {
            'resolve_url': partial(resolve_sass_url, theme_files),
        }

        sass_gen = SassGenerator(
            input_dir=sass_dir,
            output_dir=output_dir,
            download_root=download_root,
            debug=config.mode == Mode.development,
            apply_hash=config.mode == Mode.production,
            custom_functions=custom_functions,
            extra_importers=[(0, pygments_importer)]
        )
        try:
            sass_gen()
        except GrablibError as e:
            raise HarrierProblem('error generating sass') from e
        log_msg = True
        count = sass_gen._files_generated

    log_msg and log_complete(start, 'sass built', count)
    return count


PYGMENTS_PREFIX = 'pygments/'


def pygments_importer(path: str):
    if not path.startswith(PYGMENTS_PREFIX):
        return
    style_name = path[len(PYGMENTS_PREFIX):]
    formatter = HtmlFormatter(style=style_name)
    return [(f'pygments/{style_name}.css', formatter.get_style_defs('.hi'))]


def copy_assets(config: Config):
    start = time()
    in_dir = config.theme_dir / 'assets'
    if not in_dir.is_dir():
        return
    out_dir = config.dist_dir / config.dist_dir_assets
    out_dir.relative_to(config.dist_dir)
    copied = 0
    for in_path in in_dir.glob('**/*'):
        out_path = out_dir / in_path.relative_to(in_dir)
        if config.mode == Mode.production:
            out_path = insert_hash(out_path, in_path.read_bytes())
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(in_path, out_path)
        copied += 1
    logger.debug('copied %d theme assets from "%s" to "%s"',
                 copied, in_dir.relative_to(config.source_dir), out_dir.relative_to(config.dist_dir))

    copied and log_complete(start, 'theme assets copied', copied)
    return copied


def assets_grablib(config: Config):
    copy_assets(config)
    run_grablib(config)


def webpack_configuration(config: Config, watch: bool):
    if not config.webpack or not config.webpack.run:
        return None, None

    wp = config.webpack
    prod = config.mode == Mode.production
    output_filename = wp.prod_output_filename if prod else wp.dev_output_filename
    # ./ is required to satisfy webpack when files are inside the "--context" directory
    args = (
        wp.cli,
        '--context', config.source_dir,
        '--entry', f'./{wp.entry.relative_to(config.source_dir)}',
        '--output-path', wp.output_path,
        output_filename and '--output-filename', output_filename,
        '--devtool', 'source-map',
        '--mode', config.mode.value,
        watch and '--watch',
        prod and '--optimize-minimize',
        wp.config and '--config',
        wp.config and f'./{wp.config.relative_to(config.source_dir)}',
    )
    env = dict(**os.environ, **{
        'NODE_ENV': config.mode.value,
        # 'HARRIER_CONFIG': json.dumps(config.dict())  # TODO
    })
    return [str(a) for a in args if a], env


def run_webpack(config: Config):
    start = time()
    args, env = webpack_configuration(config, False)
    if not args:
        return

    cmd = ' '.join(args)
    kwargs = dict(check=True, cwd=config.source_dir, env=env)
    logger.debug('webpack command "%s"', cmd)
    capture_output = not logger.isEnabledFor(logging.DEBUG)
    if capture_output:
        kwargs.update(stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf8')
        args += '--json',
    try:
        p = subprocess.run(args, **kwargs)
    except subprocess.CalledProcessError as e:
        logger.warning('error running webpack "%s", returncode %s\nstdout: %s\nstderr: %s',
                       cmd, e.returncode, e.output, e.stderr)
        raise HarrierProblem('error running webpack') from e
    else:
        count = 1
        if capture_output:
            try:
                output = json.loads(p.stdout[p.stdout.find('{'):])
            except ValueError:
                # happens when the webpack config script writes to standout including a "{"
                pass
            else:
                count = len(output['assets'])
        log_complete(start, 'webpack built', count)
        return count


async def start_webpack_watch(config: Config):
    args, env = webpack_configuration(config, True)
    if args:
        cmd = ' '.join(args)
        logger.info('running webpack ...')
        logger.debug('webpack command "%s"', cmd)
        return await asyncio.create_subprocess_exec(*args, cwd=config.source_dir, env=env)


def find_theme_files(config: Config):
    check_dirs = (
        config.dist_dir / config.dist_dir_sass,
        config.dist_dir / config.dist_dir_assets,
        config.webpack.output_path
    )
    d = {}
    for dir in check_dirs:
        if dir.is_dir():
            for p in dir.glob('**/*'):
                if p.is_file():
                    rel_path = str(p.relative_to(config.dist_dir))
                    path_name = rel_path
                    if config.mode == Mode.production:
                        path_name = re.sub('\.[a-f0-9]{7,20}\.', '.', rel_path)
                        path_name = re.sub('\.[a-f0-9]{7,20}$', '', path_name)
                    d[path_name] = rel_path
    return d


def resolve_sass_url(theme_files, path):
    # TODO try more things, raise error on failure
    return f'"{theme_files.get(path) or path}"'
