import biopipe.termchart


def terminal_bar_chart_test():
    data = [
        ('Looooooooong label A', 125.2),
        ('Short label B', 132.3),
        ('Loooooooooooooooong label C', 250.63),
        ('D', 100.2),
    ]

    biopipe.termchart.terminal_bar_chart(data, sorted=True)
