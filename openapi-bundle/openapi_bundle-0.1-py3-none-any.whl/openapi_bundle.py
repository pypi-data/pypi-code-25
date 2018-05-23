# coding: utf-8

import click
import os
import sys
import json
import yaml

__all__ = ["bundle"]


def get_file_ext(file_path):
    _, ext = os.path.splitext(file_path)
    return ext.lower()


class BundleError(click.ClickException):
    pass


class UnknownFileTypeError(BundleError):
    def __init__(self, file_path):
        super(UnknownFileTypeError, self).__init__(
            "%s is not a json or yaml file" % file_path)


class RefIsNoneError(BundleError):
    def __init__(self, file_path):
        super(RefIsNoneError, self).__init__(
            "%s: value of $ref is not a string."
            "Make sure local $ref (started with #) is quoted"
            % file_path)


def resolve(file_path, data):
    if isinstance(data, list):
        for k, v in enumerate(data):
            data[k] = resolve(file_path, v)
    elif isinstance(data, dict):
        base_dir = os.path.dirname(file_path)
        if "$ref" in data:
            link = data["$ref"]
            if not isinstance(link, str):
                raise RefIsNoneError(file_path)
            elif link.startswith("#"):  # ignore local ref
                pass
            elif os.path.isabs(link):
                return load_json_or_yaml(link)
            else:
                return load_json_or_yaml(os.path.join(base_dir, link))
        else:
            for k, v in data.items():
                data[k] = resolve(file_path, v)

    return data


def load_json_or_yaml(abs_file_path):
    ext = get_file_ext(abs_file_path)
    with open(abs_file_path, "rt", encoding="utf-8") as f:
        if ext == ".json":
            data = json.load(f)
        elif ext == ".yaml":
            data = yaml.load(f)
        else:
            raise UnknownFileTypeError(abs_file_path)

        return resolve(abs_file_path, data)


def bundle(entry):
    return load_json_or_yaml(os.path.abspath(entry))


@click.command("openapi-bundle")
@click.option("-j", "--json", "output_format", flag_value="json", help="output json")
@click.option("-y", "--yaml", "output_format", flag_value="yaml", help="output yaml")
@click.option("--auto", "output_format", flag_value="auto", default=True, help="output same format as entry file")
@click.argument("entry", type=click.Path(exists=True, resolve_path=True), required=False)
def cli(output_format, entry):
    """This script combine multiple json or yaml files
     into a single readable OpenAPI specification.

    ENTRY could be a directory or a file (json or yaml).
    If it is a directory, index.json or index.yaml will be used.

    ENTRY can be omitted, current working directory will be assumed.

    All files including referenced files MUST be utf-8 encoded.
    """

    if entry is None:
        entry = os.getcwd()

    if os.path.isdir(entry):
        index_json = os.path.join(entry, "index.json")
        index_yaml = os.path.join(entry, "index.yaml")
        if os.path.isfile(index_json):
            entry = index_json
        elif os.path.isfile(index_yaml):
            entry = index_yaml
        else:
            raise click.BadArgumentUsage("index.json or index.yaml not found!")

    if output_format is "auto":
        ext = get_file_ext(entry)
        if ext == ".json":
            output_format = "json"
        elif ext == ".yaml":
            output_format = "yaml"
        else:
            raise UnknownFileTypeError(entry)

    api = bundle(entry)
    if output_format == "json":
        json.dump(api, fp=sys.stdout, ensure_ascii=False, indent=2)
    else:
        yaml.dump(api, stream=sys.stdout, allow_unicode=True)


if __name__ == '__main__':
    cli()
