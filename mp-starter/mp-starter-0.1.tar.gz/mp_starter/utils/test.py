"""Testing utilities for mp-starter."""

from mp_starter.cli.main import StarterTestApp
from cement.utils.test import *


class StarterTestCase(CementTestCase):
    app_class = StarterTestApp

    def setUp(self):
        """Override setup actions (for every test)."""
        super(StarterTestCase, self).setUp()

    def tearDown(self):
        """Override teardown actions (for every test)."""
        super(StarterTestCase, self).tearDown()

