"""this is a function test"""


def print_lol(the_list):
    """this function check list."""
    
    for item in the_list:
        if isinstance(item, list):
            print_lol(item)
        else:
            print(item)
