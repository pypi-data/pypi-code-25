from pytrello.api import decorators

LABEL_COLORS = ['yellow', 'purple', 'blue', 'red', 'green', 'orange', 'black',
                'sky', 'pink', 'lime', 'null']


@decorators.basic_api
def get_label(label_id):
    pass


@decorators.basic_api
def update_label(label_id):
    pass


@decorators.basic_api
def update_label_color(label_id, value):
    pass


@decorators.basic_api
def update_label_name(label_id, value):
    pass


@decorators.basic_api
def create_label(name, color, idBoard):
    pass


@decorators.basic_api
def delete_label(label_id):
    pass
