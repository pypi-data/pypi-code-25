import yaml


def load_settings(file_path):
    with open(file_path + 'settings.yaml', 'rb') as settings_file:
        yaml_settings = settings_file.read()
        settings = yaml.load(yaml_settings)

    return settings
