from abc import ABCMeta
from abc import abstractmethod


class FirewallResourceDriverInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def run_custom_command(self, context, custom_command):
        pass

    @abstractmethod
    def run_custom_config_command(self, context, custom_command):
        pass

    @abstractmethod
    def save(self, context, folder_path, configuration_type):
        pass

    @abstractmethod
    def restore(self, context, path, configuration_type, restore_method):
        pass

    @abstractmethod
    def get_inventory(self, context):
        pass

    @abstractmethod
    def orchestration_restore(self, context, saved_artifact_info, custom_params):
        pass

    @abstractmethod
    def orchestration_save(self, context, mode, custom_params):
        pass

    @abstractmethod
    def health_check(self, context):
        pass

    @abstractmethod
    def load_firmware(self, context, path):
        pass

    @abstractmethod
    def shutdown(self, context):
        pass
