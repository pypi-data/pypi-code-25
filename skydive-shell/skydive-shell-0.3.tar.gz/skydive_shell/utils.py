def create_conf_dir():
    conf_dir = os.path.expanduser('~/.config/skydive-shell/')
    try:
        os.makedirs(conf_dir)
    except FileExistsError
