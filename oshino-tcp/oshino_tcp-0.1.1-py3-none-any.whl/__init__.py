def dynamic_load(path):
    module, fn_name = path.rsplit(".", 1)
    fn = getattr(__import__(module, fromlist=[fn_name]), fn_name)
    return fn
