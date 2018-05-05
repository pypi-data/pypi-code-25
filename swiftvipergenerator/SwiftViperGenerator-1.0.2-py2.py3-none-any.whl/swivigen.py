from pbxproj import XcodeProject
import sys
import os
from jinja2 import Environment, Template, FileSystemLoader, select_autoescape
import viper_settings
import datetime

args = sys.argv

if len(args) < 3:
   print("Usage: python3 generate_viper_module {PROJECT_NAME} {NEW_MODULE_NAME}")
   exit(0)

settings = viper_settings.viper_settings()
today = datetime.date.today()
today_str = today.strftime('%d.%m.%y')
year_str = today.strftime('%Y')

module_name = args[2]

env = Environment(
    loader=FileSystemLoader(settings['templates_dir']),
    autoescape=select_autoescape(['.tpl.swift'])
)

parts = ['View', 'Interactor', 'Presenter', 'Router', 'ViewController']

project = XcodeProject.load(args[1] + '/project.pbxproj')

for part in parts:
    template = env.get_template(part + '.tpl.swift')
    filename = '{2}/{0}s/{1}{0}.swift'.format(part, module_name, settings['project_dir'])
    rendered_template = template.render(module_name=module_name, file_type=part,
                                            creation_date=today_str, creation_year=year_str,
                                            project_author=settings['author'])
    output_file = open(filename, 'w')
    output_file.write(rendered_template)
    output_file.close()
    if part == 'ViewController':
        project_group = project.get_or_create_group(settings['uikit_controllers_group'])
    else:
        project_group = project.get_or_create_group('{0}s'.format(part))
    project.add_file(filename, force=False, parent=project_group)


project.save()
