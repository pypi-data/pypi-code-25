# encoding: utf-8

import logging_helper
from future.utils import with_metaclass
from abc import abstractmethod, ABCMeta
from configurationutil import DefaultInheritableConstant, Configuration
from uiutil import BaseFrame, Button, Position, Separator, Label, Combobox, TextEntry, Switch
from uiutil.tk_names import E, W, S, EW, showerror

logging = logging_helper.setup_logging()


class AddEditConfigFrame(with_metaclass(ABCMeta, BaseFrame)):

    BUTTON_WIDTH = 12

    CONFIG_ROOT = None

    def __init__(self,
                 selected_record=None,
                 edit=False,
                 cfg=Configuration,
                 *args,
                 **kwargs):

        BaseFrame.__init__(self, *args, **kwargs)

        self.edit = edit

        self._cfg = cfg()

        self.fields = {}

        if selected_record:
            key = u'{cfg}.{int}'.format(cfg=self.CONFIG_ROOT,
                                        int=selected_record)
            self._selected_record_name = selected_record
            self.selected_record = self._cfg[key]

        else:
            self._selected_record_name = u''
            self.selected_record = None

        self._draw()

        Separator(row=Position.NEXT,
                  column=Position.START,
                  columnspan=2)

        self._build_button_frame()

        self.nice_grid()

    @property
    def selected_record_name(self):
        return self._selected_record_name if self.edit else self._name.value

    def add_field(self,
                  field,
                  label,
                  widget,
                  **kwargs):

        Label(text=label,
              row=Position.NEXT,
              column=Position.START,
              sticky=E)

        self.fields[field] = widget(row=Position.CURRENT,
                                    column=Position.NEXT,
                                    sticky=EW,
                                    **kwargs)

        self.bind_events(control=self.fields[field],
                         events=(u'<Return>',
                                 u'<Tab>',
                                 u'<KP_Enter>',
                                 u'<FocusOut>'),
                         function=self._field_changed)

    def _draw(self):

        if self.edit:
            Label(text=self._selected_record_name,
                  font=u'-size 18',
                  row=Position.START,
                  column=Position.START,
                  sticky=EW)

        else:
            Label(text=u'Name:',
                  row=Position.START,
                  column=Position.START,
                  sticky=E)

            self._name = TextEntry(value=u'',
                                   row=Position.CURRENT,
                                   column=Position.NEXT,
                                   sticky=EW)

        Separator(row=Position.NEXT,
                  column=Position.START,
                  columnspan=2)

        self.draw_config_fields()

    @abstractmethod
    def draw_config_fields(self):

        """ Draw the config entry fields. """

        pass

    def _build_button_frame(self):

        self.button_frame = BaseFrame(row=Position.NEXT,
                                      column=Position.START,
                                      sticky=(E, W, S),
                                      columnspan=2)

        Button(frame=self.button_frame,
               text=u'Cancel',
               width=self.BUTTON_WIDTH,
               command=self._cancel,
               row=Position.NEXT,
               column=Position.START,
               sticky=EW)

        self._save_button = Button(frame=self.button_frame,
                                   text=u'Save',
                                   width=self.BUTTON_WIDTH,
                                   command=self._save,
                                   row=Position.CURRENT,
                                   column=Position.NEXT,
                                   sticky=EW)

        self.button_frame.nice_grid()

    def _field_changed(self,
                       var=None):

        """ Called when return / tab / enter is pressed in or focus is moved away from a field. """

        pass

    @abstractmethod
    def save_config(self):

        """ prepare the defaults dict for saving.  Should return a dict. """

        return {}

    def _save(self):

        try:
            if not self.selected_record_name:
                raise ValueError(u'Name cannot be blank!')

            new_record = self.save_config()

            key = u'{cfg}.{ep}'.format(cfg=self.CONFIG_ROOT,
                                       ep=self.selected_record_name)

            self._cfg[key] = new_record

            self.parent.master.exit()

        except Exception as err:
            logging.error(u'Cannot save record')
            logging.exception(err)
            showerror(title=u'Save Failed',
                      message=u'Cannot Save: {err}'.format(err=err))

    def _cancel(self):
        self.parent.master.exit()
