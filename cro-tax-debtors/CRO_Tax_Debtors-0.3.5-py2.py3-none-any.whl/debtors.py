class Debtors(object):

    def __init__(self, spider=None, save_handler=None,
                 screen=None, category_data=None):
        self._spider = spider
        self._screen = screen
        self._save_handler = save_handler
        self._category_data = category_data

    def screener(self, name, debt):
        self._screen(category=self._category_data['title'],
                     name=name,
                     debt=debt,
                     limit=self._category_data['toplist_limit'],
                     color=self._category_data['color'])

    def run(self, print_in_terminal=True):
        for item in self._spider.parse():

            # save debtor
            name, debt = self._save_handler.save(item.data)

            # print everything on terminal
            if print_in_terminal:
                self.screener(name, debt)

    def find(self, name):
        for debtor in self._save_handler.find(name):
            self.screener(debtor[self._category_data['item']],
                          debtor[self._category_data['debt_key']])

        for debtor in self._save_handler.find_by_key(name):
            self.screener(debtor[self._category_data['item']],
                          debtor[self._category_data['debt_key']])

    def delete(self):
        self._save_handler.delete()


class Item:

    def __init__(self):
        self.data = {}

    def __setitem__(self, key, value):
        self.data[key] = value

    def __eq__(self, other):
        return len(self.data.keys()) > 0


class CategoryDone(Exception):
    pass
