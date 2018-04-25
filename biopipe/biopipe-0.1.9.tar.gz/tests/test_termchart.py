import biopipe.termchart


def test_terminal_bar_chart():
    data = [
        ('Looooooooong label A', 125.2),
        ('Short label B', 132.3),
        ('Loooooooooooooooong label C', 250.63),
        ('D', 100.2),
    ]

    biopipe.termchart.terminal_bar_chart(data, sort=True)
