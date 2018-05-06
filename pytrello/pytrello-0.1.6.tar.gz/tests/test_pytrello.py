
from pytrello.cli import main


def test_main():
    main([])


def test_comment():
    main(['comment', '-b', 'pytrello', '-c', 'test', 'card', '-i', 'From', 'test_comment'])


# def test_addlabel():
    # main(['addlabel', '-b', 'pytrello', '-c', 'test', 'card', '-n', 'urgent'])
