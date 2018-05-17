import cProfile, inspect, io, pstats, random
import django.core.exceptions

from operator import attrgetter
from pathlib import Path, PurePosixPath
from .config import MindsightConfig
from .store import SampleStore


class Middleware(object):
    def __init__(self, get_response):
        self.get_response = get_response
        self._config = MindsightConfig()

        if self._config.MINDSIGHT_AGENT_URL is None:
            raise django.core.exceptions.MiddleWareNotUsed

        if self._config.MINDSIGHT_SAMPLE_PROBABILITY < 0.0:
            raise django.core.exceptions.MiddleWareNotUsed

        self._store = SampleStore(
            self._config.MINDSIGHT_AGENT_URL,
            send_after=self._config.MINDSIGHT_SEND_AFTER,
            send_timeout=self._config.MINDSIGHT_SEND_TIMEOUT)


    def _must_profile(self):
        if self._config.MINDSIGHT_SAMPLE_PROBABILITY >= 1.0:
            return True
        elif random.random() < self._config.MINDSIGHT_SAMPLE_PROBABILITY:
            return True

        return False

    
    def _in_project(self, root, stat):
        return inspect.iscode(stat.code) and \
            root in Path(stat.code.co_filename).parents


    def _full_fn_name(self, stat):
        p = PurePosixPath(stat.code.co_filename)
        rel_no_ext = p.relative_to(self._config.MINDSIGHT_ROOT).with_suffix('')
        return str(rel_no_ext).replace('/', '.') + '.' + stat.code.co_name


    def _process_profile(self, profile):
        root = Path(self._config.MINDSIGHT_ROOT)

        all_stats = sorted(profile.getstats(), key=attrgetter('totaltime'), reverse=True)
        stats = [s for s in all_stats if self._in_project(root, s)]
        
        for stat in stats:
            fn_name = self._full_fn_name(stat)
            ncalls = int(stat.totaltime / self._config.MINDSIGHT_SAMPLE_INTERVAL)

            if ncalls > 0:
                self._store.record(fn_name, ncalls=ncalls)


    def __call__(self, request):
        profile = None
        response = None

        if self._must_profile():
            profile = cProfile.Profile()
            response = profile.runcall(self.get_response, request)
        else:
            response = self.get_response(request)

        if profile is not None:
            self._process_profile(profile)

        return response
