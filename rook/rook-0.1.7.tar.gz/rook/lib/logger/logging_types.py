class LogType:
    name_to_type = {}

    def __init__(self, name, log_type):
        self.log_type = log_type
        self.name = name
        LogType.name_to_type[name] = log_type

    @staticmethod
    def get_type(name):
        return LogType.name_to_type.get(name)


CURRENT_USER = LogType("currentUser", str)
ASSET_NAME = LogType("assetName", str)
ASSET_ID = LogType("assetId", str)
metric = LogType("metric", float)
ORG_ID = LogType("org_id", str)
