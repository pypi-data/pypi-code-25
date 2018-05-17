import os
import argparse
import json

from PPMSplot import plot
from PPMSplot.parser import parse_file, extract_columns


parser = argparse.ArgumentParser(description='Plot PPMS .dat files columnwise')

parser.add_argument('config', metavar='F', type=str, nargs='?',
                    help='filepath of config JSON file')

def main():
    args = parser.parse_args()
    
    try:
        assert args.config
    except:
        print('Invalid syntax')
        parser.print_help()
        quit()

    try:
        with open(args.config, 'r') as config_file:
            config = json.load(config_file)
    except json.decoder.JSONDecodeError as e:
        print('Config file has invalid syntax')
        print(e)
        quit()

    file_data = []
    for file_config in config['files']:
            file_data.append(parse_file(file_config))

    plot(config, file_data)

if __name__ == "__main__":
    main()
