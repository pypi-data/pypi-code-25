class Endpoint:
    def __init__(self, endpoint):
        parts = endpoint['value'].split('\|')
        self.transport = endpoint['tag']
        self.order = endpoint['order']
        self.uri = parts[0]
        self.interaction = parts[1]
        self.format = parts[2]
        self.scenario = parts[3]
        self.message = parts[4]
        self.compressed = parts[5]
