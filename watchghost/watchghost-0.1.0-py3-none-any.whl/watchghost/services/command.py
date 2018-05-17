import asyncio
from collections import OrderedDict


class Run:
    config = {
        'timeout': 10,
        'command': []
    }

    @staticmethod
    async def check(server, config):
        assert config['command']
        command = [
            c.format(server=server, config=config) for c in config['command']
        ]

        p = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        return await treat_process(p, config, command)


class Shell:
    config = {
        'timeout': 10,
        'command': '',
        'status': OrderedDict([
            ('error', [{'return_code': 2}]),
            ('warning', [{'return_code': 1}]),
            ('info', [{'return_code': 0}]),
            ('critical', [{}]),
        ]),
    }

    @staticmethod
    async def check(server, config):
        assert config['command']
        command = config['command'].format(server=server, config=config)

        p = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return await treat_process(p, config, command)


async def treat_process(p, config, command):
    try:
        return_code = await asyncio.wait_for(
            p.wait(), config['timeout']
        )
        ok = not return_code
        timeout = False
        stdout = await p.stdout.read()
        stderr = await p.stderr.read()
    except asyncio.TimeoutError:
        ok = False
        timeout = True
        return_code = None
        stdout = None
        stderr = None

    return {
        "ok": ok,
        'timeout': timeout,
        'stdout': stdout,
        'stderr': stderr,
        'command': command,
        'return_code': return_code,
    }
