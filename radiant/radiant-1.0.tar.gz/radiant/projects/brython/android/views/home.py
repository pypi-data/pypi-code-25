from browser import window, document
from mdcframework import Template

from pythoncore import PythonCore
Piton = PythonCore()


########################################################################
class Events:
    """"""

    #----------------------------------------------------------------------
    def connect(self):
        """"""

        #self.menu_icon.bind("click", lambda :self.menu.mdc.toggle())




########################################################################
class Home(Events):
    """"""

    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        self.main = parent

        self.main.mdc_drawer.mdc.close()
        self.main.container.clear()

        self.container = self.build()
        self.connect()


    #----------------------------------------------------------------------
    def show(self):
        """"""

        return self.container



    #----------------------------------------------------------------------
    def build(self):
        """"""
        container = Template.DIV()

        self.cells = {}


        self.mdc_toolbar = Template.Toolbar(title="Scientific Piton", class_="mdc-toolbar--fixed")
        self.mdc_toolbar.select('.mdc-toolbar__menu-icon')[0].bind('click', self.main.mdc_drawer.mdc.open)
        container <= self.mdc_toolbar

        self.button_fab = Template.ButtonFab('bug_report', class_="piton-float_button")
        container <= self.button_fab

        try:
            window.update_all()
        except:
            pass

        Template.attach()


        return container


