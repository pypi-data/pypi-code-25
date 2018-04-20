import os
import jinja2
import pathlib


PATH = pathlib.Path(os.path.dirname(os.path.realpath(__file__)))
TEMPLATE_PATH = PATH / 'templates' / 'ini'
TEMPLATE_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(str(TEMPLATE_PATH)))


def install_folder(project_path):
    folder_path = project_path / 'scopus'
    if not folder_path.exists():
        folder_path.mkdir()


def install_config(
        project_path,
        file_name='config.py',
        template_name='config.j2'
):
    file_path = project_path / 'scopus' / file_name
    template = TEMPLATE_ENV.get_template(template_name)
    content = template.render()
    with file_path.open(mode='w+') as file:
        file.write(content)


def install_authors(
        project_path,
        file_name='authors.ini',
        template_name='authors.j2'
):
    file_path = project_path / 'scopus' / file_name
    template = TEMPLATE_ENV.get_template(template_name)
    content = template.render()
    with file_path.open(mode='w+') as file:
        file.write(content)
