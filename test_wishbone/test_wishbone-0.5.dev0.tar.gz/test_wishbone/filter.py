from wishbone.module import FlowModule


class HigherLower(FlowModule):

    def __init__(self, actor_config, base=50, source='data.articles'):
        FlowModule.__init__(self, actor_config)

        self.base = base
        self.source = source[0]['article1']

        self.pool.createQueue("inbox")
        self.pool.createQueue("higher")
        self.pool.createQueue("lower")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        if not isinstance(event.get(self.source), int):
            raise TypeError("Event source total is not type integer")

        if event.get(self.source) > self.base:
            self.submit(event, self.pool.queue.higher)
        elif event.get(self.source) < self.base:
            self.submit(event, self.pool.queue.lower)
