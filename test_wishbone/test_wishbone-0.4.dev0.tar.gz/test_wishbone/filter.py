from wishbone.module import FlowModule


class HigherLower(FlowModule):

    def __init__(self, actor_config, base=100, source='data.total'):
        FlowModule.__init__(self, actor_config)

        self.base = base
        self.source = source

        self.pool.createQueue("inbox")
        self.pool.createQueue("higher")
        self.pool.createQueue("lower")
        self.pool.createQueue("equal")
        self.registerConsumer(self.consume, "inbox")

    def consume(self, event):

        if not isinstance(event.get(self.source), int):
            raise TypeError("Event source total is not type integer")

        if event.get(self.source) > self.base:
            self.submit(event, self.pool.queue.higher)
        elif event.get(self.source) < self.base:
            self.submit(event, self.pool.queue.lower)
        else:
            self.submit(event, self.pool.queue.equal)
