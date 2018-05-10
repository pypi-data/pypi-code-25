import click
from termcolor import cprint
from pyfiglet import figlet_format


class Screen(object):

    def __init__(self):
        self._keyword = None
        self._all_count = None
        self.data = {
            'toplist': {},
            'counters': {},
            'width': {},
            'colors': {}
        }

    def keyword(self, keyword):
        self._keyword = keyword

    def __call__(self, category, name, debt, limit, color, all_count):
        self.set_toplist(category, name, debt, limit)
        self.set_counter(category)
        self.set_color(category, color)
        self._print(limit)
        self._all_count = all_count

    def set_toplist(self, category, name, debt, limit):
        if category not in self.data['toplist']:
            self.data['toplist'][category] = []

        self.data['toplist'][category].append((name, debt))

        self.data['toplist'][category] = sorted(self.data['toplist'][category],
                                                key=lambda debtor: float(debtor[1]
                                                                         .replace('.', '')
                                                                         .replace(',', '.')),
                                                reverse=True)
        if len(self.data['toplist'][category]) > limit:
            self.data['toplist'][category].pop()

        if category not in self.data['width']:
            self.data['width'][category] = 0

        for name, debt in self.data['toplist'][category]:
            w = len(name)
            if w > self.data['width'][category]:
                self.data['width'][category] = w

    def set_counter(self, category):
        if category not in self.data['counters']:
            self.data['counters'][category] = 0

        self.data['counters'][category] += 1

    def set_color(self, category, color):
        self.data['colors'][category] = color

    def _print(self, limit):
        click.clear()

        cprint(figlet_format('Croatian Tax Debtors', width=120), 'red')

        click.echo()

        categories = self.data['counters'].keys()
        number_of_categories = len(categories)

        screen_line_parts = []
        for cat in self.data['width'].keys():
            screen_line_parts.append('-'*(self.data['width'][cat]+16))
            screen_line_parts.append(' '*4)
        screen_line = ''.join(screen_line_parts)

        if self._all_count:
            all_count = '/' + str(self._all_count)
        else:
            all_count = ''

        for i, category in enumerate(categories):
            cat_width = self.data['width'][category]+20
            nl = True if i+1 >= number_of_categories else False

            color = self.data['colors'][category]
            category += ' (' + str(self.data['counters'][category]) + all_count + ')'
            click.secho(category.upper() + (' '*(cat_width-len(category))), nl=nl, fg=color)

        click.echo(screen_line)

        cat_line_width = {category: 0 for category in categories}

        for j in range(int(limit)):
            for i, category in enumerate(categories):

                if len(self.data['toplist'][category]) <= j:
                    click.echo(' '*cat_line_width[category])
                else:
                    cat_width = self.data['width'][category]
                    nl = True if i+1 >= number_of_categories else False

                    color = self.data['colors'][category]
                    debtor = self.data['toplist'][category][j]

                    dots = '.'*(cat_width-len(debtor[0]))
                    line = click.style(debtor[0], fg=color) + ' ' + \
                        click.style(dots, dim=True, fg=color) + ' ' + \
                        click.style(debtor[1], fg=color)

                    line_len = len(debtor[0])+len(dots)+len(debtor[1])+2
                    click.echo(line + ' '*((cat_width+20)-line_len), nl=nl)

                    cat_line_width[category] = len(line)

        click.echo(screen_line)
        click.echo()
