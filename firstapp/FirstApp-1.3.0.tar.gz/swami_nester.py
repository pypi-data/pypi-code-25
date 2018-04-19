

def print_lol(my_list, is_indenting_required=False, level=0):
    """This nester class checks for the provided list.
    Iterates given list"""
    print("is:" + str(is_indenting_required))
    for each_item in my_list:
        """If given list element has inner list, then
        let's iterate this list too & 
        find out elements"""
        if isinstance(each_item, list):
            print_lol(each_item, is_indenting_required, level + 1)
        else:
            if is_indenting_required:
                for tab_stop in range(level):
                    print("\t", end='')
            print(each_item)


movies = ["The Holy Grail", 1975, "Terry Jones & Terry Gilliam", 91, ["Graham Chapman", ["Michael Palin",
                                                                                         "John Cleese", "Terry Gilliam",
                                                                                         "Eric Idle", "Terry Jones"]]]
print_lol(movies, False, 5)
