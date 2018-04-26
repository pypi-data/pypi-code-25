class Modules:
    some_list = {}

    def setItem(self, name, item):
        self.some_list[name] = item


class someUI(Modules):
    index = -1

    def __init__(self):
        super().__init__()
        someUI.index += 1
        self.curr_count = "someUI" + someUI.index

    def setItem(self, _item):
        super().setItem(self.curr_count, _item)


class strat(Modules):
    index = -1

    def __init__(self):
        super().__init__()
        strat.index += 1
        self.curr_count = "strat" + someUI.index

    def setItem(self, _item):
        super().setItem(self.curr_count, _item)


f = someUI()
f.setItem('item')
f.setItem('item2')
g = someUI()
g.setItem('item3')
g.setItem('item4')
h = strat()
h.setItem('item5')
pass
