import requests

'''test url in list'''
def print_list(the_list):

    for each_item in the_list:
        if isinstance (each_item, list):
            print_list(each_item, end=" status: ")
            r = requests.get('{}'.format(each_item))
            print(r.status_code)
        else:
            print(each_item, end=" status: ")
            r = requests.get('{}'.format(each_item))
            print(r.status_code)

