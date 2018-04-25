

class BaseTaskManager:

    @staticmethod
    def get_task_instance(config, message_or_response, type_):
        raise NotImplementedError
