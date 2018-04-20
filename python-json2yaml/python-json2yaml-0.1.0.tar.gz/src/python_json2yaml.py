import os
import json
import yaml
import click


@click.command()
@click.option("--input-encoding", default="utf-8")
@click.option("--output-encoding", default="utf-8")
@click.argument("src", type=click.File("rb"), default="-")
@click.argument("dst", type=click.File("wb"), default="-")
def json2yaml(input_encoding, output_encoding, src, dst):
    data = src.read()
    if os.sys.version.startswith("3."):
        data = data.decode(input_encoding)
    data = json.loads(data)
    text = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    if os.sys.version.startswith("3."):
        text = text.encode(output_encoding)
    dst.write(text)


@click.command()
@click.option("--input-encoding", default="utf-8")
@click.option("--output-encoding", default="utf-8")
@click.argument("src", type=click.File("rb"), default="-")
@click.argument("dst", type=click.File("wb"), default="-")
def yaml2json(input_encoding, output_encoding, src, dst):
    data = src.read()
    if os.sys.version.startswith("3."):
        data = data.decode(input_encoding)    
    data = yaml.load(data)
    text = json.dumps(data, ensure_ascii=False)
    text = text.encode(output_encoding)
    dst.write(text)
