class PatchType(object):
    """Class representing a PATCH request to Kinto.

    Kinto understands different PATCH requests, which can be
    represented by subclasses of this class.

    A PATCH request is interpreted according to its content-type,
    which applies to all parts of the request body, which typically
    include changes to the request's ``data`` (the resource being
    modified) and its ``permissions``.
    """
    pass


class BasicPatch(PatchType):
    """Class representing a default "attribute merge" PATCH.

    In this kind of patch, attributes in the request replace
    attributes in the original object.

    This kind of PATCH is documented at e.g.
    http://docs.kinto-storage.org/en/stable/api/1.x/records.html#attributes-merge.
    """

    content_type = 'application/json'

    def __init__(self, data=None, permissions=None):
        """BasicPatch(data)

        :param data: the fields and values that should be replaced on
            the resource itself
        :type data: dict
        :param permissions: the fields and values that should be
            replaced on the permissions of the resource
        :type permissions: dict
        """
        self.data = data
        self.permissions = permissions

    @property
    def body(self):
        ret = {}
        if self.data is not None:
            ret['data'] = self.data
        if self.permissions is not None:
            ret['permissions'] = self.permissions

        return ret


class MergePatch(PatchType):
    """Class representing a "JSON merge".

    In this kind of patch, JSON objects are merged recursively, and
    setting a field to None will remove it from the original object.

    This kind of PATCH is documented at e.g.
    http://docs.kinto-storage.org/en/stable/api/1.x/records.html?highlight=JSON%20merge#attributes-merge.

    Note that although this patch type receives both data and
    permissions, using merge-patch semantics on permissions might not
    work (see https://github.com/Kinto/kinto/issues/1322).
    """

    content_type = 'application/merge-patch+json'

    def __init__(self, data=None, permissions=None):
        """MergePatch(data)

        :param data: the fields and values that should be merged on
            the resource itself
        :type data: dict
        :param permissions: the fields and values that should be
            merged on the permissions of the resource
        :type permissions: dict
        """
        self.data = data
        self.permissions = permissions

    @property
    def body(self):
        ret = {}
        if self.data is not None:
            ret['data'] = self.data
        if self.permissions is not None:
            ret['permissions'] = self.permissions

        return ret


class JSONPatch(PatchType):
    """Class representing a JSON Patch PATCH.

    In this kind of patch, a set of operations are sent to the server,
    which applies them in order.

    This kind of PATCH is documented at e.g.
    http://docs.kinto-storage.org/en/stable/api/1.x/records.html#json-patch-operations.
    """

    content_type = 'application/json-patch+json'

    def __init__(self, operations):
        """JSONPatch(operations)

        Takes a list of operations to apply.  Operations should be
        written as though applied at the root of an object with
        ``data`` and ``permissions`` fields, which correspond to the
        data of the resource and the permissions of the resource,
        respectively.  N.B. The fields of the ``permissions`` object
        are each Python ``set`` objects represented in JSON as
        ``Arrays``, so e.g. the index ``/permissions/read/fxa:Alice``
        represents the principal ``fxa:Alice``.

        :param operations: the operations that should be performed, as
            dicts
        :type operations: list
        """
        self.body = operations
