def move_list_element_to_front(arr, element):
    arr.insert(0, arr.pop(arr.index(element)))


def move_list_element_to_end(arr, element):
    arr.insert(len(arr), arr.pop(arr.index(element)))
