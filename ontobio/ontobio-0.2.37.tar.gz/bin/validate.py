import click
import json
import os
import yaml
import requests
import gzip
import urllib
import re

from functools import wraps

from ontobio.ontol_factory import OntologyFactory
from ontobio.io.gafparser import GafParser
from ontobio.io.assocwriter import GafWriter
from ontobio.io.assocwriter import GpadWriter
from ontobio.io import assocparser
from ontobio.io import gafgpibridge
from ontobio.io import entitywriter
from ontobio.rdfgen import assoc_rdfgen


from typing import Dict

def thispath():
    os.path.normpath(os.path.abspath(__file__))

def gzips(file_function):

    @wraps(file_function)
    def wrapper(*args, **kwargs):
        output_file = file_function(*args, **kwargs)
        if isinstance(output_file, list):
            for o in output_file:
                zipup(o)
        else:
            zipup(output_file)

        return output_file

    return wrapper

def zipup(file_path):
    click.echo("Zipping {}".format(file_path))
    path, filename = os.path.split(file_path)
    zipname = "{}.gz".format(filename)
    target = os.path.join(path, zipname)

    def chunk_gen():
        with open(target, "rb") as p:
            while True:
                chunk = p.read()
                if not chunk:
                    break
                yield chunk

    with gzip.open(target, "wb") as tf:
        with click.progressbar(iterable=chunk_gen()) as chunks:
            for chunk in chunks:
                tf.write(chunk)

def find(l, finder):
    filtered = [n for n in l if finder(n)]
    if len(filtered) == 0:
        return None
    else:
        return filtered[0]

def metadata_file(metadata, group) -> Dict:
    metadata_yaml = os.path.join(metadata, "datasets", "{}.yaml".format(group))
    try:
        with open(metadata_yaml, "r") as group_data:
            click.echo("Found {group} metadata at {path}".format(group=group, path=metadata_yaml))
            return yaml.load(group_data)
    except Exception as e:
        raise click.ClickException("Could not find or read {}: {}".format(metadata_yaml, str(e)))


def download_source_gafs(group_metadata, target_dir, exclusions=[]):
    gaf_urls = { data["dataset"]: data["source"] for data in group_metadata["datasets"] if data["type"] == "gaf" and data["dataset"] not in exclusions}

    downloaded_paths = {}
    for dataset, gaf_url in gaf_urls.items():
        path = os.path.join(target_dir, "groups", dataset, "{}-src.gaf.gz".format(dataset))
        os.makedirs(os.path.split(path)[0], exist_ok=True)

        click.echo("Downloading source gaf to {}".format(path))
        if urllib.parse.urlparse(gaf_url)[0] == "ftp":
            urllib.request.urlretrieve(gaf_url, path)
        else:
            response = requests.get(gaf_url, stream=True)
            content_length = int(response.headers.get("Content-Length", None))

            with open(path, "wb") as downloaded:
                with click.progressbar(iterable=response.iter_content(chunk_size=512 * 1024), length=content_length, show_percent=True) as chunks:
                    for chunk in chunks:
                        if chunk:
                            downloaded.write(chunk)

        downloaded_paths[dataset] = path

    return downloaded_paths

def check_and_download_paint_source(paint_metadata, dataset, target_dir):
    paint_dataset = find(paint_metadata["datasets"], lambda d: d["dataset"] == "paint_{}".format(dataset))
    if paint_dataset is None:
        return None

    path = os.path.join(target_dir, "groups", dataset, "{}-src.gaf.gz".format(paint_dataset["dataset"]))
    click.echo("Downloading paint to {}".format(path))
    urllib.request.urlretrieve(paint_dataset["source"], path)
    unzipped = os.path.join(os.path.split(path)[0], "{}-src.gaf".format(paint_dataset["dataset"]))
    unzip(path, unzipped)
    return unzipped


def unzip(path, target):
    click.echo("Unzipping {}".format(path))
    def chunk_gen():
        with gzip.open(path, "rb") as p:
            while True:
                chunk = p.read(size=512 * 1024)
                if not chunk:
                    break
                yield chunk

    with open(target, "wb") as tf:
        with click.progressbar(iterable=chunk_gen()) as chunks:
            for chunk in chunks:
                tf.write(chunk)

def produce_gaf(dataset, source_gaf, ontology_graph, gpipath=None):
    filtered_associations = open(os.path.join(os.path.split(source_gaf)[0], "{}_noiea.gaf".format(dataset)), "w")

    config = assocparser.AssocParserConfig(
        ontology=ontology_graph,
        filter_out_evidence=["IEA"],
        filtered_evidence_file=filtered_associations,
        gpi_authority_path=gpipath
    )
    validated_gaf_path = os.path.join(os.path.split(source_gaf)[0], "{}_valid.gaf".format(dataset))
    outfile = open(validated_gaf_path, "w")
    gafwriter = GafWriter(file=outfile)

    click.echo("Validating source GAF: {}".format(source_gaf))
    parser = GafParser(config=config)
    with open(source_gaf) as sg:
        lines = sum(1 for line in sg)

    with open(source_gaf) as gaf:
        with click.progressbar(iterable=parser.association_generator(file=gaf), length=lines) as associations:
            for assoc in associations:
                gafwriter.write_assoc(assoc)

    outfile.close()
    filtered_associations.close()

    with open(os.path.join(os.path.split(source_gaf)[0], "{}.report.md".format(dataset)), "w") as report_md:
        report_md.write(parser.report.to_markdown())

    with open(os.path.join(os.path.split(source_gaf)[0], "{}.report.json".format(dataset)), "w") as report_json:
        report_json.write(json.dumps(parser.report.to_report_json()))

    return [validated_gaf_path, filtered_associations.name]

@gzips
def produce_gpi(dataset, target_dir, ontology_graph):

    def conversion_gen(gaf_file, gafparser):
        cache = []
        for association in gafparser.association_generator(file=gaf_file):
            entity = bridge.convert_association(association)
            if entity not in cache:
                cache.append(entity)
                yield entity
            else:
                continue

    click.echo("No GPI in metadata, building from GAF")
    gaf_path = os.path.join(target_dir, "groups", dataset, "{}.gaf".format(dataset))
    gafparser = GafParser()
    gafparser.config = assocparser.AssocParserConfig(
        ontology=ontology_graph
    )
    bridge = gafgpibridge.GafGpiBridge()
    gpi_path = os.path.join(target_dir, "groups", dataset, "{}.gpi".format(dataset))

    with open(gaf_path) as sg:
        lines = sum(1 for line in sg)

    with open(gaf_path) as gf:
        with open(gpi_path, "w") as gpifile:
            gpiwriter = entitywriter.GpiWriter(file=gpifile)
            with click.progressbar(iterable=conversion_gen(gf, gafparser)) as entities:
                for entity in entities:
                    if entity is not None:
                        gpiwriter.write_entity(entity)

    return gpi_path

@gzips
def make_products(dataset, target_dir, gaf_path, products, ontology_graph):
    gafparser = GafParser()
    gafparser.config = assocparser.AssocParserConfig(
        ontology=ontology_graph
    )

    with open(gaf_path) as sg:
        lines = sum(1 for line in sg)

    product_files = {
        "gpad": open(os.path.join(target_dir, "groups", dataset, "{dataset}.gpad".format(dataset=dataset)), "w"),
        "gpi": open(os.path.join(target_dir, "groups", dataset, "{dataset}.gpi".format(dataset=dataset)), "w")
    }

    # def write_gpi_entity(association, bridge, gpiwriter):
    with open(gaf_path) as gf:
        # gpi info:
        click.echo("Using {} as the gaf to build data products with".format(gaf_path))
        if products["gpi"]:
            click.echo("Setting up {}".format(product_files["gpi"].name))
            bridge = gafgpibridge.GafGpiBridge()
            gpiwriter = entitywriter.GpiWriter(file=product_files["gpi"])
            gpi_cache = []

        if products["gpad"]:
            click.echo("Setting up {}".format(product_files["gpad"].name))
            gpadwriter = GpadWriter(file=product_files["gpad"])

        click.echo("Making products...")
        with click.progressbar(iterable=gafparser.association_generator(file=gf), length=lines) as associations:
            for association in associations:
                if products["gpi"]:
                    entity = bridge.convert_association(association)
                    if entity not in gpi_cache and entity is not None:
                        gpi_cache.append(entity)
                        gpiwriter.write_entity(entity)

                if products["gpad"]:
                    gpadwriter.write_assoc(association)

        # After we run through associations
        for f in product_files.values():
            f.close()

    return [f.name for f in product_files.values()]

@gzips
def produce_ttl(dataset, target_dir, gaf_path, ontology_graph):
    gafparser = GafParser()
    gafparser.config = assocparser.AssocParserConfig(
        ontology=ontology_graph
    )

    with open(gaf_path) as sg:
        lines = sum(1 for line in sg)

    ttl_path = os.path.join(target_dir, "groups", dataset, "{dataset}_cam.ttl".format(dataset=dataset))
    click.echo("Producing ttl: {}".format(ttl_path))
    rdf_writer = assoc_rdfgen.TurtleRdfWriter()
    transformer = assoc_rdfgen.CamRdfTransform(writer=rdf_writer)
    parser_config = assocparser.AssocParserConfig(ontology=ontology_graph)

    with open(gaf_path) as gf:
        with click.progressbar(iterable=gafparser.association_generator(file=gf), length=lines) as associations:
            for association in associations:
                if "header" not in association or not association["header"]:
                    transformer.provenance()
                    transformer.translate(association)

    with open(ttl_path, "wb") as ttl:
        click.echo("Writing ttl to disk")
        rdf_writer.serialize(destination=ttl)

    return ttl_path

@gzips
def merge_mod_and_paint(mod_gaf_path, paint_gaf_path):

    def header_and_annotations(gaf_file):
        headers = []
        annotations = []

        for line in gaf_file.readlines():
            if line.startswith("!"):
                headers.append(line)
            else:
                annotations.append(line)

        return (headers, annotations)

    def make_paint_header(header, filename: str):
        return ["! merged_from " + os.path.basename(filename) + ": " + line.split("!")[1].strip() for line in header if not re.match("![\s]*gaf.?version", line) ]

    dirs, name = os.path.split(mod_gaf_path)
    merged_path = os.path.join(dirs, "{}.gaf".format(name.split(".")[0]))
    with open(mod_gaf_path) as mod, open(paint_gaf_path) as paint:
        mod_header, mod_annotations = header_and_annotations(mod)
        paint_header, paint_annotations = header_and_annotations(paint)

        all_lines = mod_header + make_paint_header(paint_header, paint_gaf_path) + mod_annotations + paint_annotations

        with open(merged_path, "w") as merged_file:
            merged_file.write("\n".join(all_lines))

    return merged_path


@click.group()
def cli():
    pass

@cli.command()
@click.argument("group")
@click.option("--metadata", "-m", type=click.Path(), required=True)
@click.option("--gaf", default=True, is_flag=True)
@click.option("--gpi", default=False, is_flag=True)
@click.option("--gpad", default=False, is_flag=True)
@click.option("--ttl", default=False, is_flag=True)
@click.option("--target", "-t", type=click.Path(), required=True)
@click.option("--ontology", "-o", type=click.Path(exists=True), required=False)
@click.option("--exclude", "-x", multiple=True)
def produce(group, metadata, gaf, gpi, gpad, ttl, target, ontology, exclude):
    click.echo("Building {}".format(group))

    products = {
        "gaf": gaf,
        "gpi": gpi,
        "gpad": gpad,
        "ttl": ttl
    }
    click.echo("Making products {}.".format(", ".join([key for key in products if products[key]])))
    absolute_target = os.path.abspath(target)
    os.makedirs(os.path.join(absolute_target, "groups"), exist_ok=True)
    click.echo("Products will go in {}".format(absolute_target))
    absolute_metadata = os.path.abspath(metadata)

    group_metadata = metadata_file(absolute_metadata, group)
    click.echo("Loading ontology: {}...".format(ontology))
    ontology_graph = OntologyFactory().create(ontology)

    source_gaf_zips = download_source_gafs(group_metadata, absolute_target, exclusions=exclude)
    source_gafs = {zip_path: os.path.join(absolute_target, "groups", dataset, "{}-src.gaf".format(dataset)) for dataset, zip_path in source_gaf_zips.items()}
    for source_zip, source_gaf in source_gafs.items():
        unzip(source_zip, source_gaf)

    paint_metadata = metadata_file(absolute_metadata, "paint")

    made = []
    if products["gaf"]:
        for dataset in source_gaf_zips.keys():
            gafzip = source_gaf_zips[dataset]
            source_gaf = source_gafs[gafzip]
            valid_gaf = produce_gaf(dataset, source_gaf, ontology_graph)

            make_products(dataset, absolute_target, valid_gaf, products, ontology_graph)

            paint_src_gaf = check_and_download_paint_source(paint_metadata, dataset, absolute_target)
            paint_gaf = produce_gaf("paint_{}".format(dataset), paint_src_gaf, ontology_graph, gpipath=os.path.join(absolute_target, "groups", dataset, "{}.gpi".format(dataset)))
            merged_path = merge_mod_and_paint(valid_gaf, paint_gaf)

            if products["ttl"]:
                produce_ttl(dataset, absolute_target, merged_path, ontology_graph)


@cli.command()
@click.argument("group")
@click.argument("dataset")
@click.option("--metadata", "-m", type=click.Path(), required=True)
@click.option("--target", type=click.Path(), required=True)
@click.option("--ontology", type=click.Path(), required=True)
def paint(group, dataset, metadata, target, ontology):
    absolute_metadata = os.path.abspath(metadata)
    absolute_target = os.path.abspath(target)
    os.makedirs(os.path.join(absolute_target, "groups"), exist_ok=True)
    paint_metadata = metadata_file(absolute_metadata, "paint")
    paint_src_gaf = check_and_download_paint_source(paint_metadata, dataset, absolute_target)

    click.echo("Loading ontology: {}...".format(ontology))
    ontology_graph = OntologyFactory().create(ontology)

    gpi_path = os.path.join(absolute_target, "groups", dataset, "{}.gpi".format(dataset))
    click.echo("Using GPI at {}".format(gpi_path))
    paint_gaf = produce_gaf("paint_{}".format(dataset), paint_src_gaf, ontology_graph, gpipath=gpi_path)



if __name__ == "__main__":
    cli()
