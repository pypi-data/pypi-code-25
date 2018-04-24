from controllers.docker_controller import logger
from controllers.docker_wrapper import DockerWrapper
import asyncio


class StatGenerator:
    def __init__(self, container):
        self.container = container
        self.docker_client = DockerWrapper.get()
        logger.debug('stats_generator enter')

    async def __anext__(self):
        await asyncio.sleep(0)
        cont = self.container.reload()
        if cont is None or cont.status == 'exited':
            raise StopAsyncIteration
        return self._stats(cont)

    def __aiter__(self):
        return self

    def _stats(self, cont):
        stat = cont.stats()

        # https://github.com/moby/moby/blob/eb131c5383db8cac633919f82abad86c99bffbe5/cli/command/container/stats_helpers.go#L175
        def mem_usage():
            return stat['memory_stats']['usage'], stat['memory_stats']['limit']

        # https://github.com/moby/moby/blob/eb131c5383db8cac633919f82abad86c99bffbe5/cli/command/container/stats_helpers.go#L175
        def cpu_usage():
            cpu_percent = 0.0
            pre_cpu = stat['precpu_stats']['cpu_usage']['total_usage']
            pre_system = stat['precpu_stats']['system_cpu_usage']
            cur_system = stat['cpu_stats']['system_cpu_usage']
            cur_cpu = stat['cpu_stats']['cpu_usage']['total_usage']
            cpu_delta = cur_cpu - pre_cpu
            system_delta = cur_system - pre_system
            cpu_count = len(stat['cpu_stats']['cpu_usage']['percpu_usage'])
            if cpu_delta > 0 and system_delta > 0:
                cpu_percent = (cpu_delta / system_delta) * cpu_count * 100
            return cpu_count, cpu_percent

        if stat is None:
            return
        mem_usage, mem_limit = mem_usage()
        cpu_count, cpu_percent = cpu_usage()
        shares = self.container.attrs['HostConfig']['NanoCpus'] / 1000000000.0
        x = {
            'id': stat['id'],
            'cpu': {
                'usage': round(cpu_percent, 2),
                'count': cpu_count,
                'shares': shares,
                'of_shares': round(cpu_percent / shares, 2)
            },
            'mem': {
                'usage': round((mem_usage * 100.0) / mem_limit, 2),
                'limit': round(mem_limit, 2),
            }
        }
        return x
