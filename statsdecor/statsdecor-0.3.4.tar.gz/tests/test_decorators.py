import statsdecor.decorators as decorators
import statsdecor
from tests.conftest import stub_client
from mock import MagicMock
from statsdecor.clients import (
    DogStatsdClient,
    StatsdClient
)


NO_TAGS = None


def assert_arguments(args, kwargs):
    assert ('some', 'thing') == args
    assert {'key': 'value'} == kwargs


class BaseDecoratorTestCase(object):

    def test_increment__no_tags(self):
        @decorators.increment('a.metric')
        def test_fn(*args, **kwargs):
            assert_arguments(args, kwargs)

        with stub_client(self.client_class, 'statsdecor.decorators.client') as stub:
            test_fn('some', 'thing', key='value')
            stub.client.incr.assert_called_with('a.metric', tags=NO_TAGS)

    def test_increment__with_tags(self):
        @decorators.increment('a.metric', tags=self.tags)
        def test_fn(*args, **kwargs):
            assert_arguments(args, kwargs)

        with stub_client(self.client_class, 'statsdecor.decorators.client') as stub:
            test_fn('some', 'thing', key='value')
            stub.client.incr.assert_called_with('a.metric', tags=self.tags)

    def test_decrement__no_tags(self):
        @decorators.decrement('a.metric')
        def test_fn(*args, **kwargs):
            assert_arguments(args, kwargs)

        with stub_client(self.client_class, 'statsdecor.decorators.client') as stub:
            test_fn('some', 'thing', key='value')
            stub.client.decr.assert_called_with('a.metric', tags=NO_TAGS)

    def test_decrement__with_tags(self):
        @decorators.decrement('a.metric', tags=self.tags)
        def test_fn(*args, **kwargs):
            assert_arguments(args, kwargs)

        with stub_client(self.client_class, 'statsdecor.decorators.client') as stub:
            test_fn('some', 'thing', key='value')
            stub.client.decr.assert_called_with('a.metric', tags=self.tags)

    def test_timed__no_tags(self):
        @decorators.timed('a.metric')
        def test_fn(*args, **kwargs):
            assert_arguments(args, kwargs)

        with stub_client(self.client_class, 'statsdecor.decorators.client') as stub:
            # Stub out the timing context manager.
            stub.client.timer.return_value = MagicMock()
            test_fn('some', 'thing', key='value')
            stub.client.timer.assert_called_with('a.metric', tags=NO_TAGS)

    def test_timed__with_tags(self):
        @decorators.timed('a.metric', tags=self.tags)
        def test_fn(*args, **kwargs):
            assert_arguments(args, kwargs)

        with stub_client(self.client_class, 'statsdecor.decorators.client') as stub:
            # Stub out the timing context manager.
            stub.client.timer.return_value = MagicMock()
            test_fn('some', 'thing', key='value')
            stub.client.timer.assert_called_with('a.metric', tags=self.tags)

class TestStatsdDefaultClient(BaseDecoratorTestCase):
    def setup(self):
        self.tags = ['StatsClient_doesnt_do_tags!']
        self.client_class = StatsdClient
        statsdecor.configure()

class TestDogStatsdClient(BaseDecoratorTestCase):
    def setup(self):
        self.tags = ['DogStatsd_does_tags!']
        self.vendor = 'datadog'
        self.client_class = DogStatsdClient
        statsdecor.configure(vendor=self.vendor)
