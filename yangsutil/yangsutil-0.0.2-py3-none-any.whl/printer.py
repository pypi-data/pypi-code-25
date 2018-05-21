import json


class Printer:
    @staticmethod
    def json(json_thing, is_show=True, ):
        if type(json_thing) is str:
            json_type = json.loads(json_thing)

        elif type(json_thing) is bytes:
            json_type = json.loads(json_thing.decode('utf-8'))

        else:
            json_type = json_thing

        print_string = '\n%s' % (json.dumps(json_type, sort_keys=True, indent=4))

        if is_show is True:
            print(print_string)

        return print_string

    @staticmethod
    def list(list_thing, is_show=True):

        print_string = '\n'
        for item in list_thing:
            print_string += '%s\n' % str(item)

        if is_show is True:
            print(print_string)

        return print_string
