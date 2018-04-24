import sys, os
import argparse
from pbxproj import XcodeProject
from jinja2 import Environment, Template, FileSystemLoader, select_autoescape
import datetime

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--init',
                        help='add needed base Swift files into specified project',
                        action='store_true')
    parser.add_argument('project', help='XCode project that should be modified')
    parser.add_argument('module', help='name for new viper module')
    args = parser.parse_args()
    
    sys.path.append(os.getcwd()) 
    
    import viper_settings

    settings = viper_settings.viper_settings()
    today = datetime.date.today()
    today_str = today.strftime('%d.%m.%y')
    year_str = today.strftime('%Y')

    module_name = args.module

    template_dir = settings['templates_dir']
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if template_dir == '{Templates}':
        template_dir = dir_path + '/Templates'
    
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(['.tpl.swift'])
        )

    parts = ['View', 'Interactor', 'Presenter', 'Router', 'ViewController']

    project = XcodeProject.load(args.project + '/project.pbxproj')

    if args.init:
        common_dir = dir_path + '/Common'
        common_group = project.get_or_create_group('ViperCommon')
        for dirname, dirnames, filenames in os.walk(common_dir):
            for filename in filenames:
                project.add_file(os.path.join(dirname, filename), force=False,
                                    parent=common_group)
    
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

if __name__ == 'swivigen':
    main()
