import win32console

_stdin = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)


# taken from https://stackoverflow.com/a/32156249
# thanks to mbdevpl(https://stackoverflow.com/users/4973698/mbdevpl)
def input_edit_text(prompt, text_to_edit=''):
    keys = []
    for c in str(text_to_edit):
        evt = win32console.PyINPUT_RECORDType(win32console.KEY_EVENT)
        evt.Char = c
        evt.RepeatCount = 1
        evt.KeyDown = True
        keys.append(evt)

    _stdin.WriteConsoleInput(keys)
    return input(prompt)
