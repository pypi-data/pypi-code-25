# -*- coding: utf-8 -*-
import json
import os
import random
import shutil
import sys

import click

from spell_cli.api_constants import (
    get_machine_types,
    get_machine_type_default,
)
from spell_cli.exceptions import (
    ExitException,
    SPELL_INVALID_CONFIG,
)
from spell_cli.utils import (
    LazyChoice,
    parse_utils,
    truncate_string,
    tabulate_rows,
)
from spell_cli.utils.parse_utils import ParseException


@click.group(name="jupyter", short_help="Manage installed Jupyter kernels")
def jupyter():
    try:
        # Ignore these unused imports in flake8 because they're just used to check if modules exist
        from jupyter_client.kernelspec import KernelSpecManager  # noqa
        from IPython.utils.tempdir import TemporaryDirectory     # noqa
    except ImportError:
        raise ExitException('Failed to import jupyter, install with "pip install jupyter"')


@jupyter.command(name="install", help="Install a Jupyter kernel locally")
@click.option("-n", "--name",
              help='Kernel display name, defaults to "Spell <MACHINE_TYPE>"')
@click.option("--system", is_flag=True,
              help="Install to the system install directory (requires root)")
@click.option("-t", "--machine-type",
              type=LazyChoice(get_machine_types), default=get_machine_type_default,
              help="Machine type to run on")
@click.option("--pip", "pip_packages",
              help="Dependency to install using pip", multiple=True)
@click.option("--apt", "apt_packages",
              help="Dependency to install using apt", multiple=True)
@click.option("--conda-env", help="Name of conda environment name to activate")
@click.option("--conda-file",
              help="Path to conda environment file",
              type=click.Path(exists=True, file_okay=True, dir_okay=False, writable=False, readable=True))
@click.option("-e", "--env", "envvars", multiple=True,
              help="Define an environment variable")
@click.option("-m", "--mount", "raw_resources", multiple=True,
              help="Mount a resource")
def install(name, system, machine_type, pip_packages, apt_packages, conda_env, conda_file, envvars, raw_resources):
    from jupyter_client.kernelspec import KernelSpecManager
    from IPython.utils.tempdir import TemporaryDirectory

    argv = [
        sys.executable,
        "-m", "spell_cli.jupyter.spell_kernel",
        "--machine-type", machine_type,
    ]

    # Pip packages
    for pip_package in pip_packages:
        argv += [
            "--pip", pip_package,
        ]

    # Apt packages
    for apt_package in apt_packages:
        argv += [
            "--apt", apt_package,
        ]

    # Conda dependencies
    conda_file_contents = None
    if conda_file is not None and conda_env is None:
        raise ExitException("A conda environment name is required if a conda environment file is specified.",
                            SPELL_INVALID_CONFIG)
    if conda_env is not None and conda_file is None:
        raise ExitException("A conda environment file is required if a conda environment name is specified.",
                            SPELL_INVALID_CONFIG)
    if conda_file is not None and conda_env is not None:
        with open(conda_file) as conda_f:
            conda_file_contents = conda_f.read()
        argv += [
            "--conda-file", conda_file_contents,
            "--conda-env", conda_env,
        ]

    # Environment variables
    for envvar in envvars:
        argv += [
            "--env", envvar,
        ]

    # Mounts
    try:
        parse_utils.parse_attached_resources(raw_resources)
    except ParseException as e:
        raise ExitException(click.wrap_text(
            "Incorrect formatting of mount '{}', it must be <resource_path>[:<mount_path>]".format(e.token)),
            SPELL_INVALID_CONFIG)
    for resource in raw_resources:
        argv += [
            "--mount", resource,
        ]

    # Connection file
    argv.append("{connection_file}")

    # Display name
    if name is None:
        default = "Spell {}".format(machine_type)
        name = click.prompt("Enter a display name for the kernel", default=default)

    kernel_spec = {
        "argv": argv,
        "display_name": name,
        "mounts": raw_resources,
        "pip": pip_packages,
        "apt": apt_packages,
        "conda_file": conda_file_contents if conda_file_contents else "",
        "conda_env": conda_env if conda_env else "",
        "envvars": envvars,
    }

    # Install kernel
    with TemporaryDirectory() as tmpdir:
        os.chmod(tmpdir, 0o755)
        with open(os.path.join(tmpdir, "kernel.json"), "w") as kernel_file:
            json.dump(kernel_spec, kernel_file, sort_keys=True, indent=2)

        kernel_id = hex(random.getrandbits(32))[2:].rjust(8, '0')
        try:
            KernelSpecManager().install_kernel_spec(tmpdir, "spell_"+kernel_id, user=(not system))
        except OSError as e:
            if system:
                raise ExitException("Permission denied. Installing to system requires running as root")
            else:
                raise e

    click.echo("Installed kernel {} ({})".format(kernel_id, name))


@jupyter.command(name="uninstall", help="Uninstall an installed Spell kernel")
@click.argument("kernel_id")
def uninstall(kernel_id):
    from jupyter_client.kernelspec import KernelSpecManager

    installed = {
        k[6:]: v
        for k, v in KernelSpecManager().find_kernel_specs().items()
        if k.startswith("spell_")
    }
    if kernel_id not in installed.keys():
        raise ExitException("Kernel {} does not exist".format(kernel_id))

    try:
        shutil.rmtree(installed[kernel_id])
    except OSError:
        raise ExitException("Permission denied. Uninstalling system kernels requires running as root")


@jupyter.command(name="list", help="List installed Spell kernels")
def list():
    from jupyter_client.kernelspec import KernelSpecManager

    installed = {
        k: v
        for k, v in KernelSpecManager().find_kernel_specs().items()
        if k.startswith("spell_")
    }

    kernels = []
    for kernel_id, kernel_dir in installed.items():
        kernel_file = os.path.join(kernel_dir, "kernel.json")
        with open(kernel_file) as kf:
            kernel_spec = json.load(kf)

        kernels.append((
            kernel_id[6:],
            truncate_string(kernel_spec["display_name"], 15),
            truncate_string(",".join(kernel_spec["mounts"]), 30),
            truncate_string(",".join(kernel_spec["pip"]), 30),
            truncate_string(",".join(kernel_spec["apt"]), 30),
            truncate_string(kernel_spec["conda_file"], 15),
            truncate_string(kernel_spec["conda_env"], 15),
            truncate_string(",".join(kernel_spec["envvars"]), 30),
        ))

    tabulate_rows(kernels, headers=["ID", "NAME", "MOUNTS", "PIP", "APT", "CONDA FILE", "CONDA ENV", "ENV VARS"])
