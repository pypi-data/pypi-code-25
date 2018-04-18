from uiutil import BaseFrame, standalone, Combobox, Position, Label


class MyFrame(BaseFrame):

    VALUES = ["First",
              "Second",
              "Third",
              "Fourth",
              "Fifth",
              "Sixth",
              "Seventh"]

    def __init__(self,
                 **kwargs):
        super(MyFrame, self).__init__(**kwargs)

        self.cb1 = Combobox(values=self.VALUES,
                            sort=False,
                            trace=self.selection)

        self.cb2 = Combobox(values=self.VALUES,
                            sort=True,
                            row=Position.NEXT,
                            trace=self.selection)

        self.cb3 = Combobox(values=self.VALUES,
                            value=self.VALUES[1],
                            sort=Combobox.sorted_except_first_value,
                            row=Position.NEXT,
                            trace=self.selection)

        self.label = Label(row=Position.NEXT,
                           value="?")
        self.selection()

    def selection(self):
        try:
            cb1 = self.cb1.value
            cb2 = self.cb2.value
            cb3 = self.cb3.value
        except AttributeError:
            return  # Widgets not initialised
        self.label.value = ('combobox 1: {cb1}\n'
                            'combobox 2: {cb2}\n'
                            'combobox 3: {cb3}\n'
                            .format(cb1=cb1,
                                    cb2=cb2,
                                    cb3=cb3))

standalone(frame=MyFrame)
