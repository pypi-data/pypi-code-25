import os
from argparse import ArgumentParser

from serpentarium.engine.ExecutionContext import ExecutionContext
from serpentarium.engine.Runner import Runner
from serpentarium.monitoring.CompoundMonitor import CompoundMonitor
from serpentarium.util.helpers import parse_config


def main():
    parser = ArgumentParser()
    parser.add_argument('--config_path', '-c', help='Path to the config file', default=None)
    parser.add_argument('--draw', '-d', help='Flag to just draw the hierarchy', default=False)
    parser.add_argument('--draw_path', '-p', help='Image path', default="hierarchy.png")
    args = parser.parse_args()

    if args.config_path is not None:
        config_path = args.config_path
    else:
        dir_path = os.path.dirname(os.path.realpath(__file__))
        config_path = dir_path + "/config.yml"

    if not args.draw:
        runner = Runner(config_path)
        runner.run()
    else:
        config = parse_config(config_path)
        graph = ExecutionContext(mods=config['mods'], monitor=CompoundMonitor([]),
                                 monitor_polling=-1)
        graph.draw(config["name"], args.draw_path)


if __name__ == "__main__":
    # execute only if run as a script
    main()
