import tkinter
from collections import OrderedDict
from tkinter.messagebox import showwarning

from db.orm import Manager
from staff_info.gui_exceptions import TooManyItemsChecked
from .models import Employee
from .views import GuiBuilder, ToplevelBuilder, gui_table_fields, gui_labels, add_employee_labels


class GuiDirector:

    def __init__(self, parent=None):
        self.builder = None
        self.parent = parent

    def construct_gui(self, row_count, col_count, labels, toolbar1, toolbar2):
        self.builder = GuiBuilder(self.parent)
        self.builder.makeCheckbar(row_count)
        self.builder.makeTable(labels, row_count, col_count)
        self.builder.makeToolbar(row_count+1, toolbar1)
        self.builder.makeToolbar(row_count+2, toolbar2)

    def load_init_data(self, model):
        objects = model.objects
        for row, obj in zip(self.builder.row_vars, objects):  # iterate over entries & objects
            for i, col in enumerate(gui_table_fields):
                key, model = col[0], col[1]
                if key not in obj.__dict__.keys():
                    values = manager.get_related_last(obj, model)
                    keys = model.fields
                    d = dict(zip(keys, values[0]))
                    row[i].set(d[key])
                else:
                    row[i].set(obj[key])

    def __getattribute__(self, item):
        if item in ('row_vars', 'cblist'):
            return self.builder.__getattribute__(item)
        else:
            return object.__getattribute__(self, item)


class Callbacks:

    def __init__(self, director):
        self.director = director


    def onChangeAttribute(self, table, labels_dict, operation):
        try:
            toplevel = ToplevelBuilder()
            ids = takeids(self.director.cblist, self.director.row_vars)
            show_warning_for_id(ids)
            title = 'Change {} data'.format(table)
            # columns = table_descriptions[table][:]
            for item in ('id', 'idEmp', '{}_available'.format(table)):
                columns.remove(item)
            field_list = OrderedDict(zip(columns, columns))
            field_list['delta'] = 'Delta'
            btn_list = (('Commit', lambda: self.onCommit(), 'left'),
                        ('Cancel', lambda: toplevel.destroy(), 'right'),)
            toplevel.input_template(title, field_list, btn_list)
        except TooManyItemsChecked:
            showwarning('Selection WARNING', 'Select 1 Employee for this operation')

    def onAddEmployee(self):
        toplevel = ToplevelBuilder()
        title = 'Add Employee'
        labels = add_employee_labels
        btn_list = (('Commit', lambda: self.onAddEmployeeCommit(toplevel), 'left'),
                    ('Cancel', lambda: toplevel.destroy(), 'right'),)
        toplevel.input_template(title, labels, btn_list)


    def onCommit(self):
        ids = takeids(self.director.cblist, self.director.row_vars)
        print(ids)

    def onAddEmployeeCommit(self, toplevel):
        d = {}
        for k, v in toplevel.ent_dict.items():
            d[k] = v.get()
        manager.create_object(**d)
        Employee.objects = []
        run(root)
        toplevel.destroy()


    @staticmethod
    def onCancel():
        pass



def get_key(row_num, labels):
    label_text = [item[1] for item in labels]
    label_text.insert(0, 'id')

def link_labels_to_table_keys(labels, employee):
    label_text = [item[1] for item in labels]
    label_text.insert(0, 'id')

def takeids(cblist, rows_var):
    """ Take check button list and returns Employee ids for continue operation.
    Show warning message if selected 'all' button for critical operation (flag warning).
    Return tuples of (id, rownum) of check button
    """

    rowsnum = tuple([i-1 for (i, var) in enumerate(cblist) if var.get()])
    ids = tuple([(int(rows_var[i][0].get()), i+1) for i in rowsnum])
    return ids


def show_warning_for_id(ids):
    if len(ids) > 1:
        raise TooManyItemsChecked(*ids)


def shrink_label_dict(*keys, **label_dict):
    d = OrderedDict()
    print(keys)
    print(label_dict)
    for k in keys:
        if k in label_dict:
            d[k] = label_dict[k]
    return d




def run(root):

    director = GuiDirector(root)
    toolbar1 = {'1': (('Add Empl', 'left', lambda: Callbacks(director).onAddEmployee()), ('Del Empl', 'right'),),
                '4': (('Change', 'left'),),
                '5': (('Add', 'left'), ('Rem', 'right')),
                '6': (('Add', 'left'), ('Rem', 'right')),
                '7': (('Add', 'left'), ('Rem', 'right'))}
    toolbar2 = {'1': (('Salary', 'left'), ('Commission', 'right')),
                '4': (('History', 'left'),),
                '5': (('History', 'left'),),
                '6': (('History', 'left'),),
                '7': (('History', 'left'),)}
    objects = manager.get_all()
    row_count = len(objects)
    col_count = len(gui_table_fields)
    director.construct_gui(row_count, col_count, gui_labels, toolbar1, toolbar2)
    director.load_init_data(Employee)

manager = Manager(Employee)

if __name__ == '__main__':
    root = tkinter.Tk()
    run(root)
    root.mainloop()


