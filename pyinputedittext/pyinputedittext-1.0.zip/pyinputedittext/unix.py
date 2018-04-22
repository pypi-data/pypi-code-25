import readline


# taken from https://stackoverflow.com/a/2533142
# thanks to sth(https://stackoverflow.com/users/56338/sth)
def input_edit_text(prompt, text_to_edit=''):
    readline.set_startup_hook(lambda: readline.insert_text(text_to_edit))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()
