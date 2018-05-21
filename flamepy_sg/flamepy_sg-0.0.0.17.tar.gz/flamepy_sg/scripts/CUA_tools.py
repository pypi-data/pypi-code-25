import os
import traceback


from flamepy_sg.scripts.customprints.ansi_colors import sg_colors
import subprocess as sb

# PySide stuff, included with Flame default install. Quick and lazy import *
from PySide.QtCore import *
from PySide.QtGui import *
from flamepy_sg.scripts.batch_selections.batch_selections_UI import SelectionsWidget

# Snippets
from flamepy_sg.scripts.batch_snippets import mvr_back_to_beauty as _backtobeauty
from flamepy_sg.scripts.batch_snippets.btb_input_dialog import InputDialogBox

# #################
print sg_colors.grey3 + '-' * 80 + sg_colors.endc
print sg_colors.blue2 + "--- From CUA_tools ---" + sg_colors.endc


absolute_path = os.path.realpath(__file__)
root_path = '/'.join(absolute_path.split('/')[0:-2])


# adds entries to Flame contextual menu.
def getCustomUIActions():

    toolsAction1 = {}
    toolsAction1["name"] = "selections"
    toolsAction1["caption"] = "Selections"

    toolsAction2 = {}
    toolsAction2["name"] = "backtobeauty"
    toolsAction2["caption"] = "Backtobeauty"

    toolsAction3 = {}
    toolsAction3["name"] = "particles_cheatsheet"
    toolsAction3["caption"] = "Particles cheatsheet"

    toolsGroup = {}
    toolsGroup["name"] = "Tools"
    toolsGroup["actions"] = (toolsAction1, toolsAction2, toolsAction3,)

    return (toolsGroup,)


# Assign some action to the CUA (customUIAction) menu entries
def customUIAction(info, userData):

    # save, reload, and do things with nodes and compass selections
    if info['name'] == 'selections':
        import flame

        def get_selection():
            import flame

            print sg_colors.green1 + "--- def get_selection() inside CustomUiaction_selections.py ---" + sg_colors.endc
            print sg_colors.red2 + "--- remember: 2018.3 doesn't need '.get_value()', 2019 does ---" + sg_colors.endc

            try:
                return ["" + s.name + "" for s in flame.batch.selected_nodes.get_value()]  # for 2019 and up
            except:
                traceback.print_exc()
                return ["" + s.name + "" for s in flame.batch.selected_nodes]  # for 2018.3

        yamlpath = "{root}/scripts/batch_selections/saved_nodes.yaml".format(root=root_path)

        # ############
        app = QApplication.activePopupWidget()
        # we call 'save_Load_selections_UI_04c.py' giving it 2 args:
        # -> the path to the yaml file and the selected nodes list
        form = SelectionsWidget(path=yamlpath, graphSelected=get_selection)
        form.show()
        app.exec_()

    # rebuild the beauty pass using all need specific passes (diffuse, lighting, reflections, specs ...):
    # imports all passes and connect them in a predifined way.
    if info['name'] == 'backtobeauty':

        def user_input_builds_btb():
            dialog = InputDialogBox()
            dialog.show()
            if dialog.exec_():
                shot_text = str(dialog.shotName.text())
                print sg_colors.yellow1 + "shot_text: " + shot_text + sg_colors.endc
                elt_text = str(dialog.elementName.text())
                print sg_colors.yellow1 + "elt_text: " + elt_text + sg_colors.endc

                _backtobeauty.main(shot_text, elt_text)

        user_input_builds_btb()

    # open a text file: a particles cheatsheet
    if info['name'] == 'particles_cheatsheet':
        particles_cheatsheet = "{root}/scripts/text_files/Expressions_particles_reformated.txt".format(root=root_path)

        print sg_colors.grey3 + particles_cheatsheet + sg_colors.endc
        sb.call(["open", particles_cheatsheet])


print sg_colors.orange1 + "--- End of CUA_tools ---" + sg_colors.endc
print sg_colors.grey3 + '-' * 80 + sg_colors.endc
