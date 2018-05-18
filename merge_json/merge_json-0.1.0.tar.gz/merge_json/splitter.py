import json
from glob import glob

def split(input_file, output_file_pattern, name_function=None, transform_function=None, indent=None):
    content = None
    i = 0
    with open(input_file, "r") as r:
        content = json.load(r)
    if type(content) is list:
        if name_function is None:
            name_function = lambda i, obj: "item_%d" % i
            
        if transform_function is None:
            transform_function = lambda obj: obj
            
        for item in content:
            out_file = output_file_pattern % name_function(i, item)
            
            mod_item = transform_function(item)
            
            with open(out_file, "w") as w:
                json.dump(mod_item, w, indent=indent)
            i += 1
    else: # Raise error?
        print(input_file, "does not contain a JSON array")
        pass
    return i