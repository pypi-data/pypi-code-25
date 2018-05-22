
class base_list():

    def __init__(self):
        self.lItems = None

    def add_item(self, oItem):
        try:
            self.lItems.append(oItem)
        except AttributeError:
            self.lItems = [oItem]

    def get_item(self, sItemName):
        for oItem in self.lItems:
            if oItem.name == sItemName:
                return oItem
        return None


class node():

    def __init__(self, name=None, subNode=None):
        self.name = name
        self.subNode = subNode


class edge():

    def __init__(self, source=None, target=None, name=None):
        self.source = source
        self.target = target
        self.name = name


class trace():

    def __init__(self, sName):
        self.name = sName
        self.path = None

    def add_to_path(self, oEdge):
        try:
            self.path.append(oEdge)
        except AttributeError:
            self.path = [oEdge]

    def get_expanded_path(self):

        lExpandedPath = []

        for oPath in self.path:
            if isinstance(oPath, edge):
                lExpandedPath.append(oPath)
            elif isinstance(oPath, trace):
                lTracePath = oPath.get_expanded_path()
                lExpandedPath.extend(lTracePath)

        return lExpandedPath
