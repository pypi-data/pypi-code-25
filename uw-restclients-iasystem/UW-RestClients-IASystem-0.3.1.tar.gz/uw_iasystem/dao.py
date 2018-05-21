"""
Contains IASystem DAO implementations.
"""

import logging
import os
from os.path import abspath, dirname
from restclients_core.dao import DAO
from uw_iasystem.models import Evaluation


SERVICE_PREFIX = 'iasystem_'


class IASystem_UW_DAO(DAO):
    def service_name(self):
        return SERVICE_PREFIX + Evaluation.DOMAIN_SEA

    def service_mock_paths(self):
        return [abspath(os.path.join(dirname(__file__), "resources"))]


class IASystem_UWB_DAO(IASystem_UW_DAO):
    def service_name(self):
        return SERVICE_PREFIX + Evaluation.DOMAIN_BOT


class IASystem_UWT_DAO(IASystem_UW_DAO):
    def service_name(self):
        return SERVICE_PREFIX + Evaluation.DOMAIN_TAC


class IASystem_UWEO_AP_DAO(IASystem_UW_DAO):
    def service_name(self):
        return SERVICE_PREFIX + Evaluation.DOMAIN_EO_AP.replace("-", "_")


class IASystem_UWEO_IELP_DAO(IASystem_UW_DAO):
    def service_name(self):
        return SERVICE_PREFIX + Evaluation.DOMAIN_EO_IELP.replace("-", "_")


DAO_DICT = {
    "seattle": [IASystem_UW_DAO()],
    "bothell": [IASystem_UWB_DAO()],
    "tacoma": [IASystem_UWT_DAO()],
    "pce_ap": [IASystem_UWEO_AP_DAO()],
    "pce_ol": [IASystem_UWEO_AP_DAO()],
    "pce_ielp": [IASystem_UWEO_IELP_DAO()],
    "pce": [IASystem_UWEO_AP_DAO(), IASystem_UWEO_IELP_DAO()]
    }
# The pce domain list order matters.
# Number of course evaluations for AU17:
#   uweo-ap: 387
#   uweo-ielp: 28


def IASystem_DAO(domain):
    """
    domain: course section's campus, LMS-owner for PCE courses.
    exception: KeyError
    """
    if domain is None:
        raise KeyError('IASystem_DAO: domain is None')
    return DAO_DICT[domain.lower()]
