import importlib


class ObjectUtil:
    @staticmethod
    def get_class(module_name, class_name):

        try:
            m = importlib.import_module(module_name)
        except ImportError:
            return None

        try:
            c = getattr(m, class_name)
        except AttributeError:
            return None

        return c

    @staticmethod
    def get_class_by_path(class_path):
        class_path_split = class_path.split('.')

        class_name = class_path_split[-1]

        module_name = ''
        for path in class_path_split[:len(class_path_split) - 1]:
            module_name += path + '.'
        module_name = module_name[:len(module_name) - 1]

        return ObjectUtil.get_class(module_name, class_name)
