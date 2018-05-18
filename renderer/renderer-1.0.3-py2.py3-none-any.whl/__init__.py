# from renderer.serializer import SerializerClass


class StrRenderer(object):
    """
    Class that converts various data types into their bytes representation i.e str, primarily to be
    used externally by a logger or other storages external to python(db, file systems...)
    """

    def __init__(self, target='file'):
        self._target = target

    def __call__(self, _, __, event_dict):
        return self.render(event_dict, )

    def render(self, data, ):
        """
        Render various data types to strings(bytes)
        :param data: The data of type 'n':[list,dict,string,unicode]
        :return: A string (which is a series of bytes)
        :rtype :str
        """
        from renderer.bridge_context import Context
        result = Context().render(data=data, target=self._target)
        return result
