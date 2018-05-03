import click, emoji

@click.command()
def cli():
    print(emoji.emojize("Hello World Again! :fire:"))
