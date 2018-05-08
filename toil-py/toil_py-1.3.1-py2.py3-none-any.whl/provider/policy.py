# -*- coding: utf-8 -*-
"""
Example custom service
"""
import logging

import toil.provider.base
import toil

logger = logging.getLogger(__name__)


class PolicyLib(toil.provider.base.BaseProvider):
    """
    Class example

    Properties :
      config: dict with configuration data
    """

    def __init__(self, toil, config):
        super(PolicyLib, self).__init__(toil, config)

    def session(self, profile='default'):
        """
        Create session.

        Args:
          profile (str): the profile defined in config to use

        Returns:
          Session
        """
        if profile in self.config:
            self.configure_proxy()
            # dynamically load the class
            policy_class = self._toil.load_class(self.config[profile]['provider'])
            # create an instance of class
            return policy_class(self.config[profile])
        else:
            raise toil.CloudException(
                "profile '{profile}' not defined in config {config}".format(profile=profile, config=self.config))


class BasePolicySession(object):
    """
    Provides basic policy behaviour.
    """

    @property
    def total_count(self):
        return self._total_count

    @property
    def processed_count(self):
        return self._processed_count

    @property
    def compliant_count(self):
        return self._compliant_count_total_count

    @property
    def violation_count(self):
        return self._violation_count

    @property
    def error_count(self):
        return self._error_count

    @property
    def log_percent_mod(self):
        return self._log_percent_mod

    @log_percent_mod.setter
    def log_percent_mod(self, value):
        self._log_percent_mod = value

    def __init__(self, config):
        self._config = config
        self._total_count = 0
        self._processed_count = 0
        self._compliant_count = 0
        self._violation_count = 0
        self._log_percent_mod = 10
        self._error_count = 0

        super(BasePolicySession, self).__init__()

    def enforce(self, **kwargs):

        self.log_policy_action(type(self).__name__ + ' enforce')

        self.pre_enforce()

        policy_data = self.get_policy_data()

        if policy_data is not None:
            self._total_count = len(policy_data)

            for policy_record in policy_data:
                try:
                    self._processed_count += 1
                    if self.is_compliant(policy_record):
                        self._compliant_count += 1
                        self.handle_compliant(policy_record)
                    else:
                        self._violation_count += 1
                        self.handle_violation(policy_record)

                    if (self._processed_count % self._log_percent_mod) == 0:
                        percent_complete = ((self._processed_count + 0.00) / (len(policy_data) + 0.00)) * 100
                        logger.info(
                            "processed:{processed} of {total} {percent}%".format(processed=self._processed_count,
                                                                                 total=self._total_count,
                                                                                 percent=percent_complete))

                except Exception as ex:
                    self._error_count += 1
                    logger.error(ex)
                    self.handle_error(policy_record, ex)

        self.post_enforce()

    def pre_enforce(self, *args, **kwargs):
        logger.info('pre_enforce')

    def post_enforce(self, *args, **kwargs):
        logger.info('post_enforce')

    def is_compliant(self, policy_record):
        logger.info('is_compliant')
        return True

    def handle_compliant(self, policy_record):
        logger.info('handle_compliant')

    def handle_violation(self, policy_record):
        logger.info('handle_violation')

    def handle_error(self, policy_record, error):
        logger.info('handle_violation')

    def log_policy_action(self, policy_record):
        logger.info('log_policy_action')

    def get_policy_data(self):
        logger.info('get_policy_data')
        return []

    def log_policy_action(self, data):
        logger.info('log_policy_action')

    def log_policy_enforcement_message(policy_id, resource_id, is_compliant, resource_detail, violation,
                                       violation_action, message):
        logger.info('log_policy_enforcement_message')
