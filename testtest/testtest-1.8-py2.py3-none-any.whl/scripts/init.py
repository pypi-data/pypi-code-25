import click, emoji, os

@click.command()
def cli():
    if not os.path.exists('tests'):
        os.makedirs('tests')
        os.makedirs('tests/test')
        print(emoji.emojize(("create 'tests/' :snake:")))
        print("create 'tests/test'")
    else:
        print('Directory already exists')
