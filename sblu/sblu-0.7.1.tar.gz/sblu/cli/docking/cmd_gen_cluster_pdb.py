import click
import re
import sys
import logging
import json as _json

from prody import parsePDB
from prody import writePDB

from sblu.ft import (read_rotations, read_ftresults_stream,
                     apply_ftresults_atom_group, symmetrize_ftresults)

logger = logging.getLogger(__name__)

def read_clusters_stream_text(stream):
    cluster_data = {
        "radius": None,
        "min_cluster_size": None,
        "max_clusters": None,
        "clusters": []
    }

    cluster = {"center": -1, "members": []}

    for line in stream:
        line_ = line.rstrip()
        if re.match(r'^Radius', line_):
            cluster_data["radius"] = float(line_.split()[1])
        elif re.match(r'^Center', line_):
            if cluster["center"] != -1:
                cluster_data["clusters"].append(cluster)
            cluster = {"center": int(line_.split()[1]) - 1,
                       "members": []}
        elif re.match(r'^[0-9]+$', line_):
            cluster["members"].append(int(line_) - 1)
        else:
            raise ValueError("Unexpected line in clusterfile.")
    cluster_data["clusters"].append(cluster)

    return cluster_data


def read_clusters(filepath):
    with open(filepath, "r") as f:
        try:
            clusters_data = _json.load(f)
        except ValueError:
            f.seek(0)
            clusters_data = read_clusters_stream_text(f)
        return clusters_data


@click.command('gen_cluster_pdb',
               short_help="Generate pdb models for cluster centers.")
@click.argument("clusterfile", type=click.Path(exists='true'))
@click.argument("ftfile", type=click.File(mode='r'))
@click.argument("rotprm", type=click.Path(exists=True))
@click.argument("lig_file", type=click.Path(exists=True))
@click.option('-o', "--output-prefix", type=click.STRING,
              default="lig",
              help="Common prefix for output pdb files (default: lig)")
@click.option('-l', "--max-clusters", type=click.INT,
              default=None,
              help="Number of top clusters to build models for (default: all)")
@click.option('-s', "--symmetry", help="Type of symmetry")
def cli(clusterfile, ftfile, rotprm, lig_file,
        output_prefix, max_clusters, symmetry):
    if symmetry is not None and not symmetry.startswith('C'):
        logger.error('only Cn symmetry is currently supported')
        sys.exit()
    cluster_data = read_clusters(clusterfile)

    cluster_centers = [cluster["center"]
                       for cluster in cluster_data["clusters"]]

    ftresults = read_ftresults_stream(ftfile, limit=None)
    ftresults_centers = ftresults[cluster_centers][:max_clusters]
    rotations = read_rotations(rotprm)
    lig = parsePDB(lig_file)

    transformed = apply_ftresults_atom_group(lig, ftresults_centers, rotations)
    for i in range(transformed.numCoordsets()):
        model_fname = output_prefix + "." + "{:02d}".format(i)
        writePDB(model_fname, transformed, csets=[i])
    if symmetry is not None:
        #assume symmetry format is Cn or C-n, e.g. C-3 and C3 will give 3
        num_subunits = abs(int(symmetry[1:]))
        for subunit in range(2, num_subunits):
            loc_ft, loc_rot = symmetrize_ftresults(ftresults_centers,
                                                   rotations, subunit)
            transformed = apply_ftresults_atom_group(lig, loc_ft, loc_rot)
            for i in range(transformed.numCoordsets()):
                model_fname = output_prefix + "." + "{:02d}.{:d}".format(i, subunit)
                writePDB(model_fname, transformed, csets=[i])
