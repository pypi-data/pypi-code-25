import tkinter
from collections import OrderedDict

from PIL import ImageTk
from .models import Employee, Position, Timeoff, InformalVacation, Vacation, Salary, Commission

class GuiBuilder:

    def __init__(self, parent=None):
        self.parent = parent
        self.cblist = []
        self.row_vars = []

    def makeCheckbar(self, rowcount):
        for i in range(rowcount + 1):
            var = tkinter.IntVar()
            cb = tkinter.Checkbutton(self.parent, variable=var)
            cb.grid(column=0, row=i)
            self.cblist.append(var)
            if i == 0:
                cb.config(command=lambda: self.onCheckALL())

    def onCheckALL(self):    # check/unchek all checkbar items
        if self.cblist[0].get():
            [el.set(1) for el in self.cblist]
        else:
            [el.set(0) for el in self.cblist]

    def makeRefreshButton(self, filepath):
        sync_b = tkinter.Button(self.parent, command=lambda: onRefresh,
                                justify='center', width="25", height="20")  # refresh button
        syn_img = ImageTk.PhotoImage(file=filepath)
        sync_b.config(image=syn_img)
        img_b = syn_img
        sync_b.grid(column=1, row=0)
        return img_b

    def makeTable(self, labels, row_count, col_count):

        def create_label(col_num, label):
            lab = tkinter.Label(self.parent, text=label[0], width=label[1], relief='groove')
            lab.grid(row=0, column=col_num, sticky='NSEW')
            lab.config(font=(None, '10', 'bold'))
            self.parent.columnconfigure(col_num, weight=1)

        def create_entry(cols_var, row_num, col_num, width, color='light grey', justify='center'):
            """
            Creates grid of entries: Col 0 - checkbar column, col 1-n - data columns
            Column 2,3 - editable(white), others - not editable(grey)
            """
            st_var = tkinter.StringVar()
            ent = tkinter.Entry(self.parent, textvariable=st_var, bg=color, relief='sunken', justify=justify)
            ent.grid(row=row + 1, column=col, sticky='NSEW')
            ent.config(width=width)

            cols_var.append(st_var)
            if col in (2, 3):
                ent.bind('<Return>', lambda _: onEdit(st_var, row_num, col_num))
            else:
                ent.bind('<Key>', lambda _: onBindOther(st_var, row_num, col_num))
            self.parent.columnconfigure(col + 1, weight=1)

        for i, (key, label) in enumerate(labels.items()):
            create_label(i+1, label)
        self.parent.rowconfigure(0, weight=1)

        for row in range(row_count):
            col_vars = []
            for col in range(1, col_count+1):
                if col == 1:
                    create_entry(col_vars, row, col, 3)
                elif col == 2:
                    create_entry(col_vars, row, col, 30, color='white', justify='left')
                elif col == 3:
                    create_entry(col_vars, row, col, 20, color='white')
                else:
                    create_entry(col_vars, row, col, 20)
            self.row_vars.append(col_vars)
            self.parent.rowconfigure(row + 1, weight=1)

    def makeToolbar(self, row_num, toolbar_items, width="10"):
        for key in toolbar_items:
            colspan = 1
            bwidth = width
            if key == '1':
                bwidth = "25"
                colspan = 2
            frm_button = tkinter.Frame(self.parent)
            frm_button.grid(row=row_num, column=int(key), columnspan=colspan, sticky='we')
            for button in toolbar_items[key]:
                if button:
                    try:
                        btn1 = tkinter.Button(frm_button, text=button[0], command=button[2], width=bwidth)
                    except IndexError:
                        btn1 = tkinter.Button(frm_button, text=button[0], width=bwidth)
                    if button[0] in ('History', 'Change'):
                        btn1.pack(side=button[1], expand='YES', fill='x')
                    else:
                        btn1.pack(side=button[1], pady='1')


class ToplevelBuilder(tkinter.Toplevel):

    def __init__(self, parent=None):
        tkinter.Toplevel.__init__(self)
        self.parent = parent
        self.ent_dict = {}
        self.but_dict = {}

    def input_template(self, title, field_list, button_list):
        """
        Create GUI for Toplevel dialog window. Input parameters are list of entry names
        and button parameters. Created widgets (vars of widget) append to class instance
        """
        for row, (k, v) in enumerate(field_list.items()):
            tkinter.Label(self, text=v[0], justify='right', width=25).grid(row=row, column=0)
            entry_var = tkinter.StringVar()
            tkinter.Entry(self, textvariable=entry_var, width=30).grid(row=row, column=1)
            self.ent_dict[k] = entry_var
        frm = tkinter.Frame(self)
        frm.grid(row=len(field_list) + 1, column=1, columnspan=2)
        for button in button_list:
            btn = tkinter.Button(frm, text=button[0], command=button[1]).pack(side=button[2], padx=5, pady=1)
            self.but_dict[button[0]] = btn
        self.title(title)

    def show_template(self):
        pass

    def makeTable(self):
        pass

    def makeToolbar(self, toolbar_items):
        pass


def onRefresh():
    pass

def onEdit(st_var, row_num, col_num):
    pass

def onBindOther(st_var, row_num, col_num):
    pass

def create_labels(*fields):
    labels = OrderedDict()
    for item in fields:
        field, model = item[0], item[1]
        labels[field] = model.labels[field]
    return labels


# List of columns in main GUI dashboard
gui_table_fields = [('idEmp', Employee), ('fullname', Employee), ('dateOfEmp', Employee),
                    ('current_pos', Position),
                    ('timeoff_available', Timeoff),
                    ('informal_vacation_available', InformalVacation),
                    ('vacation_available', Vacation)]

# List of fields for input form to create new Employee
add_employee_table = gui_table_fields[1:] + [('comm_percent', Commission), ('current', Salary), ]
add_employee_table.insert(2, ('dob', Employee))

toolbar1 = {'1': (('Add Empl', 'left'), ('Del Empl', 'right'),),
            '4': (('Change', 'left'),),
            '5': (('Add', 'left'), ('Rem', 'right')),
            '6': (('Add', 'left'), ('Rem', 'right')),
            '7': (('Add', 'left'), ('Rem', 'right'))}
toolbar2 = {'1': (('Salary', 'left'), ('Commission', 'right')),
            '4': (('History', 'left'),),
            '5': (('History', 'left'),),
            '6': (('History', 'left'),),
            '7': (('History', 'left'),)}

gui_labels = create_labels(*gui_table_fields)
add_employee_labels = create_labels(*add_employee_table)

if __name__ == '__main__':
    root = tkinter.Tk()
    row_count = 5
    g = GuiBuilder(root)
    g.makeCheckbar(row_count)
    img = g.makeRefreshButton('./arrow_refresh.png')
    g.makeTable(gui_labels, row_count, col_count=7)
    g.makeToolbar(row_count+1, toolbar1)
    g.makeToolbar(row_count+2, toolbar2)
    root.mainloop()
