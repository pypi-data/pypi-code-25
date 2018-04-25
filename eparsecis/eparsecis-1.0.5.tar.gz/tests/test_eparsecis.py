#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_eparsecis
----------------------------------

Tests for `eparsecis` module.
"""
import os
import logging
import unittest

from EPCPyYes.core.v1_2 import template_events
from eparsecis import eparsecis


class TestParser(eparsecis.EPCISParser):

    def handle_transformation_event(
            self,
            epcis_event: template_events.TransformationEvent
    ):
        assert (len(epcis_event.error_declaration.corrective_event_ids) == 2)
        assert (epcis_event.event_id == '9db05f77-e007-41a2-a6d9-140254b7ce5a')
        assert (epcis_event.transformation_id == '391')
        for ilmd in epcis_event.ilmd:
            assert (ilmd.name == 'lotNumber' or 'itemExpirationDate')
            assert (ilmd.value == 'DL232' or '2015-12-31')


class TestEparsecis(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        logging.basicConfig(level=logging.DEBUG)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_epcis_file(self):
        curpath = os.path.dirname(__file__)
        parser = TestParser(
            os.path.join(curpath, 'data/epcis.xml'))
        parser.parse()


if __name__ == '__main__':
    unittest.main()
