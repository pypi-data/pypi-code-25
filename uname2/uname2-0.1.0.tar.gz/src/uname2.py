#!/usr/bin/env python
import platform
import click


def get_uname_info():
    info = platform.uname()
    if isinstance(info, (list, tuple)):
        class Object(object):
            pass
        result = Object()
        result.system = info[0]
        result.node = info[1]
        result.release = info[2]
        result.version = info[3]
        result.machine = info[4]
        result.processor = info[5]
        return result
    else:
        return info

@click.command()
@click.option("-a", "--all", is_flag=True, default=False, help="print all information")
@click.option("-s", "--kernel-name", is_flag=True, default=False, help="print the kernel name")
@click.option("-n", "--nodename", is_flag=True, default=False, help="print the network node hostname")
@click.option("-r", "--kernel-release", is_flag=True, default=False, help="print the kernel release")
@click.option("-v", "--kernel-version", is_flag=True, default=False, help="print the kernel version")
@click.option("-m", "--machine", is_flag=True, default=False, help="print the machine hardware name")
@click.option("-p", "--processor", is_flag=True, default=False, help="print the hardware platform or \"unknown\"")
def cli(all, kernel_name, nodename, kernel_release, kernel_version, machine, processor):
    """Print certain system information.  With no OPTION, same as -s.
    """
    if not (all or kernel_name or nodename or kernel_release or kernel_version or machine or processor):
        kernel_name = True
    info = get_uname_info()
    if all:
        line = [info.system, info.node, info.release, info.version, info.machine, info.processor]
        click.echo(" ".join(line))
    else:
        line = []
        if kernel_name:
            line.append(info.system)
        if nodename:
            line.append(info.node)
        if kernel_release:
            line.append(info.release)
        if kernel_version:
            line.append(info.version)
        if machine:
            line.append(info.machine)
        if processor:
            line.append(info.processor)
        click.echo(" ".join(line))

if __name__ == "__main__":
    cli()
