"""
Utility to export objects.
"""


class Export:
    """
    Utility to export objects.
    """

    def __init__(self, itop, class_name, query=None):
        self.itop = itop
        self.class_name = class_name
        if query is None or query == "":
            self.query = "SELECT " + class_name
        else:
            self.query = query

    def get(self):
        """
        Gets the objects data
        :return: JSON data as string
        """
        try:
            data = self.itop.get(self.class_name, self.query)
            if data['code'] != 0:
                exit(data['message'])
            found = data['message'].split(" ")[1]
            if found == "0":
                exit("No object found for {}, i won't continue".format(self.query))
            else:
                return list(data["objects"].values())
        except IOError as exception:
            exit(str(exception))

def export_data(itop, class_name, query=None):
    """
    Exports data
    :param itop: itop connection
    :param class_name: class of the objects to export
    :param query: OQL query
    :return: objects found; if no query provided, it will return all objects of the class
    """
    return Export(itop, class_name, query).get()
