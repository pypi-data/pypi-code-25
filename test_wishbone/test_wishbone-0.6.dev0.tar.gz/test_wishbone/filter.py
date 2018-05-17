from wishbone.module import FlowModule


class HigherLower(FlowModule):

    def __init__(self, actor_config, base=50, source='data.articles'):
        FlowModule.__init__(self, actor_config)
        self.base = base
        self.source = source

        self.pool.createQueue("inbox")
        self.pool.createQueue("higher")
        self.pool.createQueue("lower")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):
        if not isinstance(event.get(self.source), dict):
            raise TypeError("Event source total is not type integer")

        temp = int(event.get(self.source)['article1'])
        if temp > self.base:
            self.submit(event, self.pool.queue.higher)
        elif temp < self.base:
            self.submit(event, self.pool.queue.lower)
