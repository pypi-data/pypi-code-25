#!/usr/bin/env python3

"""
Build a directory of ConfigMap/Secret manifests, inserting data from files.

See README.rst
"""

import argparse
import base64
import errno
import json
import logging
import logging.config
import os
import os.path
import shutil
import sys

try:
    from ruamel import yaml
    ruamel = True
except ImportError:
    try:
        import yaml
        ruamel = False
    except ImportError:
        sys.stderr.write("No yaml parser available.\n")
        sys.stderr.write("Run `pip install ruamel.yaml` (recommended), ")
        sys.stderr.write("or `pip install pyyaml`\n")
        exit(1)

CONFIG_FILENAME = ".build-maps.yaml"
FILES_PREFIX = ".files"

def main():
    # Parse arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("dest", nargs="?")
    parser.add_argument("--clean", dest="clean", action="store_const", const=True, default=None)
    parser.add_argument("--no-clean", dest="clean", action="store_const", const=False, default=None)
    parser.add_argument("-q", "--quiet", dest="log_level", action="store_const", const="ERROR", default=None)
    parser.add_argument("--debug", dest="log_level", action="store_const", const="DEBUG", default=None)
    args = parser.parse_args()
    src_root = args.source
    dst_root = args.dest
    clean = args.clean
    log_level = args.log_level or "INFO"

    # Setup logging.
    config_logging(log_level)
    logger = logging.getLogger(__name__)

    if not ruamel:
        logger.warn("ruamel.yaml not available, falling back to pyyaml")
        logger.warn("For cleaner manifest outputs, run `pip install ruamel.yaml`")

    logger.debug("Args:")
    logger.debug("  * source: {}".format(src_root))
    logger.debug("  * dest: {}".format(dst_root))
    logger.debug("  * clean: {}".format(clean))
    logger.debug("  * log_level: {}".format(log_level))

    # Try to load build config from the source path.
    logger.debug("")
    config_filename = os.path.join(src_root, CONFIG_FILENAME)
    logger.debug("Loading build config {}".format(config_filename))
    try:
        with open(config_filename) as fp:
            config = yaml_load(fp)
            logger.debug("  * OK: {}".format(config))
    except IOError as exc:
        if exc.errno != errno.ENOENT:
            raise
        else:
            config = None
            logger.debug("  * Config doesn't exist")

    # If dst_root isn't passed, try to get it from the build config.
    if isinstance(config, dict) and "dest" in config:
        if dst_root is None:
            dst_root = os.path.join(src_root, config["dest"])
            logger.debug("  * dest is now: {}".format(dst_root))
        else:
            logger.debug("  * Ignoring dest: overridden on command line")
    elif dst_root is None:
        parser.error(
            "dest is a required argument as {} "
            "doesn't have a `dest` setting".format(
                os.path.join(src_root, CONFIG_FILENAME)
            )
        )

    # If --clean/--no-clean isn't passed, try to get it from the
    # build config.
    if isinstance(config, dict) and "clean" in config:
        if clean is None:
            clean = config["clean"]
            logger.debug("  * clean is now: {}".format(clean))
        else:
            logger.debug("  * Ignoring clean: overridden on command line")

    # If --clean is passed, remove current files in the dest path.
    if clean:
        logger.debug("")
        logger.debug("Cleaning dest")
        try:
            basenames = os.listdir(dst_root)
        except OSError as exc:
            if exc.errno != errno.ENOENT:
                raise
        else:
            for basename in basenames:
                filename = os.path.join(dst_root, basename)
                logger.debug("  * Deleting {}".format(filename))
                if os.path.isdir(filename):
                    shutil.rmtree(filename)
                else:
                    os.remove(filename)
    logger.debug("")

    # Walk the source directory.
    for src_path, dirnames, basenames in os.walk(src_root, topdown=True):
        # Get the equivalent path in the dest directory.
        dst_path = os.path.normpath(
            os.path.join(dst_root, os.path.relpath(src_path, src_root))
        )

        # Create the dest parent directory.
        try:
            os.makedirs(dst_path)
        except OSError as exc:
            if exc.errno != errno.EEXIST:
                raise

        # Loop through filenames in this directory.
        for basename in basenames:
            # Get the src/dst filenames.
            src_filename = os.path.join(src_path, basename)
            dst_filename = os.path.join(dst_path, basename)

            # Skip hidden files.
            if basename.startswith("."):
                logger.debug("Skipping hidden file {}".format(src_filename))
                continue

            # Skip non-manifest files.
            if not basename.endswith((".yaml", ".yml", ".json")):
                logger.debug("Skipping non-manifest file {}".format(
                    src_filename
                ))
                continue

            # Get the name of the "*.files" directory for this manifest.
            files_dirname = "{}{}".format(basename, FILES_PREFIX)

            # If the "*.files" directory doesn't exist, copy the manifest
            # verbatim and move on.
            if files_dirname not in dirnames:
                logger.info("Copying {} to {}".format(
                    src_filename,
                    dst_path
                ))
                shutil.copyfile(src_filename, dst_filename)
                continue

            # Exclude "*.files" from later os.walk iterations.
            dirnames[:] = [
                dirname
                for dirname in dirnames
                if dirname != files_dirname
            ]

            # Get the fully-qualified path of the "*.files" directory.
            files_path = os.path.join(src_path, files_dirname)

            # Get a list of "*.files" basenames.
            file_basenames = [
                file_basename
                for file_basename in os.listdir(files_path)
                if not file_basename.startswith(".")
            ]
            logger.info("Copying {} to {} with data from {}".format(
                src_filename,
                dst_path,
                ", ".join(file_basenames)
            ))

            # Load the source manifest.
            if src_filename.endswith(".json"):
                manifest = json.load(open(src_filename))
            else:
                with open(src_filename) as fp:
                    manifest = yaml_load(fp)

            # Add "*.files" contents into the manifest's "data" section.
            data = manifest.setdefault("data", {})
            for file_basename in file_basenames:
                file_filename = os.path.join(files_path, file_basename)
                file_content = open(file_filename, "rb").read()
                file_content_b64 = base64.b64encode(file_content)
                data[file_basename] = file_content_b64.decode("ascii")

            # Save the dest manifest.
            if dst_filename.endswith(".json"):
                json.dump(open(dst_filename, "w"), manifest, indent=4, sort_keys=True)
            else:
                with open(dst_filename, "w") as fp:
                    fp.write(yaml_dump(manifest))

def yaml_load(string):
    if ruamel:
        return yaml.load(string, Loader=yaml.RoundTripLoader)
    else:
        return yaml.load(string)

def yaml_dump(obj):
    if ruamel:
        return yaml.dump(obj, Dumper=yaml.RoundTripDumper)
    else:
        return yaml.dump(obj)

def config_logging(log_level):
    logging.config.dictConfig({
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(message)s"
            },
        },
        "handlers": {
            "default": {
                "formatter": "standard",
                "level": log_level,
                "class": "logging.StreamHandler",
            },
        },
        "loggers": {
            __name__: {
                "handlers": ["default"],
                "level": log_level,
                "propagate": True
            }
        }
    })

if __name__ == "__main__":
    main()
