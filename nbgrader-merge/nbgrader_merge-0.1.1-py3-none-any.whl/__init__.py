import copy
import json
import os
import logging


logger = logging.getLogger(__name__)


class NoSolutionsInFile(Exception):
    pass


def is_exercise_nb(file):
    with open(file, 'rt', encoding='utf-8') as fp:
        data = json.load(fp)
    for cell in data['cells']:
        if cell.get('metadata', {}).get('nbgrader', {}):
            return True
    return False


def merge(source, destination):
    """
    source and destination are dicts representing notebooks with nbgrader metadata
    Returns a new structure placing any solution cell in source in the destination structure
    """

    # Map solutions cells
    solutions = {}
    for cell in source['cells']:
        is_nbgrader_solution = (cell.get('metadata', {})
                                .get('nbgrader', {})
                                .get('solution', False))
        if not is_nbgrader_solution:
            continue

        if cell['metadata']['nbgrader'].get('grade_id') is None:
            raise RuntimeError('Missing id in graded cell')

        grade_id = cell['metadata']['nbgrader']['grade_id']
        solutions[grade_id] = cell

    if not solutions:
        raise NoSolutionsInFile
    
    ref = copy.deepcopy(destination)

    # Apply solution cells to destination
    for cell in ref['cells']:
        is_nbgrader_solution = (cell.get('metadata', {})
                                .get('nbgrader', {})
                                .get('solution', False))
        if not is_nbgrader_solution:
            continue

        try:
            grade_id = cell['metadata']['nbgrader']['grade_id']
        except KeyError:
            logger.warning("Cell not in source `%s`", grade_id)
            continue

        logger.debug('Merging cell `%s`', grade_id)
        cell['source'] = solutions[grade_id]['source']

    return ref


def merge_files(source_file, destination_file, output_file):
    with open(destination_file, 'rt', encoding='utf-8') as dst_fp, open(source_file, 'rt', encoding='utf-8') as src_fp:
        source = json.load(src_fp)
        destination = json.load(dst_fp)

    try:
        out = merge(source, destination)
    except NoSolutionsInFile:
        logger.warning("No solutions found in nbgrader notebook `%s`",
                       source_file)
        return

    with open(output_file, 'wt', encoding='utf-8') as fp:
        json.dump(out, fp, indent=1, ensure_ascii=False)
        fp.write('\n')


def merge_dirs(source_dir, destination_dir):
    for dirpath, dirnames, filenames in os.walk(source_dir):
        logging.debug('Walked in `%s`', dirpath)
        if os.path.basename(dirpath) == '.ipynb_checkpoints':
            logging.debug('Skipping .ipynb_checkpoints in `%s`', dirpath)
            continue

        relpath = os.path.relpath(dirpath, source_dir)

        for fname in filenames:
            if not fname.endswith('.ipynb'):
                continue

            src_file = os.path.join(dirpath, fname)
            dst_file = os.path.join(destination_dir, relpath, fname)

            if is_exercise_nb(src_file):
                logger.debug("Merging file `%s`", os.path.join(relpath, fname))
            else:
                logger.debug("Skipping file `%s`", os.path.join(relpath, fname))
                continue

            try:
                merge_files(src_file, dst_file, dst_file)
            except json.JSONDecodeError:
                logger.exception(
                    "Merge is incomplete error decoding notebooks")


