from browser import document
import framework
#from mdc import MDCBuild
from mdcframework import Template, Build

from pythoncore import PythonCore

Piton = PythonCore()

from apps import PitonCore

from home import Home


########################################################################
class Base:
    """"""

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        #print("OK")

        framework.select("title").html("Scientific Piton")

        self.views = {}

        Build.styles([
            "css/styles.css",
            ])

        Build.scripts([

           ])

        self.piton_core = PitonCore()

        self.build()
        super().__init__()



    #----------------------------------------------------------------------
    def build(self):
        """"""

        self.mdc_drawer = Template.TemporaryDrawer()
        self.mdc_drawer.select('.mdc-list')[0] <= self.sidebar()


        self.container = Template.DIV(Class="main-containder", style={"padding-top": "55px", })

        self.toolbar_elements = {}

        #document <= self.mdc_toolbar
        document <= self.mdc_drawer
        document <= self.container

        #Template.attach()





    #----------------------------------------------------------------------
    def sidebar(self):
        """"""

        style = {'color': "#757575",}

        sidebar = []



        home = Template.ListItem(text="Cells", icon='code', href='#', style=style)
        home.bind('click', lambda evt:self.set_view('Home'))
        sidebar.append(home)
        #sidebar.append(home)
        #sidebar.append(home)
        #sidebar.append(home)
        #sidebar.append(home)
        #sidebar.append(home)




        return sidebar


    #----------------------------------------------------------------------
    def set_view(self, name):
        """"""
        if name in self.views:
            self.container.clear()
            self.container <= self.views[name].show()

        else:
            view = eval(name)
            view = view(self)
            self.container.clear()
            self.container <= view.show()
            self.views[name] = view

        self.mdc_drawer.mdc.close()
        Template.attach()





main = Base()
main.set_view('Home')

try:
    document.select('.splash_loading')[0].remove()
except:
    pass


