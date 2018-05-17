from wishbone.function.module import ModuleFunction


class GrandTotal(ModuleFunction):

    def __init__(self, source='data.articles', destination='data.total'):

        self.source = source
        self.destination = destination

    def do(self, event):
        total = 0

        for article, price in event.get(self.source).items():
            total += int(price)
        event.set(total, self.destination)
        return event
