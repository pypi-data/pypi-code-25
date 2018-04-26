import argparse
import spm2olca.pack as pack
import spm2olca.parser as parser
import logging as log
import sys
import os


def get_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('csv_file', metavar='CSV File', type=str,
                    help='The SimaPro CSV file')
    ap.add_argument('-out', type=str, default=None,
                    help='name of the output file')
    ap.add_argument('-skip_unmapped', action='store_true',
                    help='skip LCIA factors of non-reference flows')
    ap.add_argument('-units', default=None,
                    help='an optional CSV file with unit mappings')
    ap.add_argument('-flows', default=None,
                    help='an optional CSV file with flow mappings')
    ap.add_argument('-log', type=str, default='error',
                    choices=['error', 'warn', 'all'],
                    help='optional logging level (default is error)')
    return ap.parse_args()


def main():
    args = get_args()
    configure_logger(args)

    file_path = args.csv_file
    p = parser.Parser()
    p.parse(file_path)

    zip_file = file_path + '.zip'
    if args.out is not None:
        zip_file = args.out

    if os.path.isfile(zip_file):
        log.warning('%s already exists and will be overwritten' % zip_file)
        os.remove(zip_file)

    unit_mapping = None
    if args.units is not None:
        unit_mapping = mappings.UnitMap(args.units)
        log.info('read %i unit mappings from %s' % (len(unit_mapping.mappings),
                                                    args.units))

    flow_mapping = None
    if args.flows is not None:
        flow_mapping = mappings.FlowMap(args.flows)
        log.info('read %i flow mappings from %s' % (len(flow_mapping.mappings),
                                                    args.flows))

    p = pack.Pack(p.methods, skip_unmapped_flows=args.skip_unmapped,
                  unit_map=unit_mapping, flow_map=flow_mapping)
    p.to(zip_file)


def configure_logger(args):
    log_level = log.ERROR
    if args.log == 'warn':
        log_level = log.WARNING
    if args.log == 'all':
        log_level = log.DEBUG
    log.basicConfig(level=log_level, format='  %(levelname)s %(message)s',
                    stream=sys.stdout)
