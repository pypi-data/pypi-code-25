import os

from flamepy_sg.modules import yaml
from flamepy_sg.scripts.customprints.ansi_colors import sg_colors

from flamepy_sg.scripts.project_config import ProjectPaths_layout
from flamepy_sg.scripts.project_config import infoStaff_layout
from flamepy_sg.scripts.project_config import ExportPresets_layout

# PySide stuff, included with Flame default install.
# quick and lazy import *
from PySide.QtCore import *
from PySide.QtGui import *

absolute_path = os.path.realpath(__file__)
root_path = '/'.join(absolute_path.split('/')[0:-2])

yaml_Pathnames_Path = "{root}/scripts/project_config/ProjectPaths_config_result.yaml".format(root=root_path)
yaml_Staff = "{root}/scripts/project_config/InfoStaff_config_result.yaml".format(root=root_path)
yaml_export_presets = "{root}/scripts/project_config/ExportPresets_result.yaml".format(root=root_path)

print sg_colors.grey3 + '-' * 80 + sg_colors.endc
print sg_colors.blue2 + "--- From CUA_config ---" + sg_colors.endc

# Import the current config. Will be used later to setText (fileFullPath) in the ExportPresetsTab class
# yaml_export_presets = '/opt/flame_dev/flame_hooks_sg/hooks_py_apps/utilities/ExportPresets_result.yaml'
# yaml_export_presets = "{root}/flame_hooks_sg/hooks_py_apps/utilities/ExportPresets_result.yaml".format(root=root_path)

with open(yaml_export_presets, 'r') as config:
    cfg = yaml.load(config)

export_preset01_name = cfg["export_preset01"]["name"]
export_preset01_path = cfg["export_preset01"]["path"]
export_preset02_name = cfg["export_preset02"]["name"]
export_preset02_path = cfg["export_preset02"]["path"]
export_preset03_name = cfg["export_preset03"]["name"]
export_preset03_path = cfg["export_preset03"]["path"]
export_preset04_name = cfg["export_preset04"]["name"]
export_preset04_path = cfg["export_preset04"]["path"]
export_preset05_name = cfg["export_preset05"]["name"]
export_preset05_path = cfg["export_preset05"]["path"]


# adds entries to Flame contextual menu.
def getCustomUIActions():

    configAction1 = {}
    configAction1["name"] = "exports_config"
    configAction1["caption"] = "Config GUI - wip"

    ConfigGroup = {}
    ConfigGroup["name"] = "Config"
    ConfigGroup["actions"] = (configAction1, )

    return (ConfigGroup,)


# Assign some action to the CUA (customUIAction) menu entries
def customUIAction(info, userData):

    if info['name'] == 'exports_config':
        print sg_colors.blue2 + "--- Begining of 'customUIAction' inside CUA_config.py ---" + sg_colors.endc
        # __appname__ = "Tab Dialog"

        # general GUI 'container'
        class TabDialog(QDialog):
            def __init__(self, parent=None):
                super(TabDialog, self).__init__(parent)

                fileInfo = QFileInfo()

                w = 800
                h = 200
                self.setMinimumSize(w, h)

                tabWidget = QTabWidget()
                tabWidget.addTab(PathsTab(fileInfo), "Project Paths")
                tabWidget.addTab(StaffTab(fileInfo), "Staff Contact Infos")
                tabWidget.addTab(ExportPresetsTab(fileInfo), "Export Presets")

                # buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
                buttonBox = QDialogButtonBox(QDialogButtonBox.Close)
                buttonBox.accepted.connect(self.accept)
                buttonBox.rejected.connect(self.reject)

                mainLayout = QVBoxLayout()
                mainLayout.addWidget(tabWidget)
                mainLayout.addWidget(buttonBox)

                self.setLayout(mainLayout)

                self.setWindowTitle("Config Utilities")

        # Project root path and project name: browse or type. Saved to ProjectPaths_config_result.yaml
        class PathsTab(QMainWindow, ProjectPaths_layout.Ui_ProjectPathsLayout):

            def __init__(self, fileInfo, parent=None):
                super(PathsTab, self).__init__(parent)

                self.setupUi(self)  # This is defined in export_hook_layout.py file automatically. It sets up layout and widgets that are defined
                self.pushButton_save.clicked.connect(self.saveYaml)  # When the button is pressed: saves the yaml config file
                self.browsePath.clicked.connect(self.browse_path)  # When the button is pressed: Execute browse_path function
                self.browseProject.clicked.connect(self.browse_project)  # When the button is pressed: Execute browse_folder function

                with open(yaml_Pathnames_Path, 'r') as config1:
                    cfg1 = yaml.load(config1)
                projects_root_path = cfg1["projects_root_path"]
                project_name = cfg1["project_name"]
                ############

                # Placeholders and/or default values
                self.projectRootPathField.setText(projects_root_path)
                self.projectNameField.setPlaceholderText(project_name)

            def browse_path(self):
                print sg_colors.green1 + "--- def browse_path(self): in class PathsTab(QMainWindow, ProjectPaths_layout.Ui_ProjectPathsLayout): inside CustomUIaction_Uililities.py ---" + sg_colors.endc
                self.projectRootPathField.clear()  # In case there are any existing elements in the list
                # execute getExistingDirectory dialog and set the directory variable to be equal to the user selected directory
                directory = QFileDialog.getExistingDirectory(self, "browse")

                if directory:  # if user didn't pick a directory don't continue
                    # self.projectNameField.saveLastOpenedDir(directory) # >>>>>>>> NOT WORKING - Crashes
                    self.projectRootPathField.setText(os.path.normpath(directory))

            def browse_project(self):
                print sg_colors.green1 + "--- def browse_path(self): in class PathsTab(QMainWindow, ProjectPaths_layout.Ui_ProjectPathsLayout): inside CustomUIaction_Uililities.py ---" + sg_colors.endc
                self.projectNameField.clear()  # In case there are any existing elements in the list
                directory = QFileDialog.getExistingDirectory(self, "browse")

                if directory:
                    self.projectNameField.setText(os.path.basename(directory))

            def store_UIcontent(self):
                pass

            # YAML = Save the yaml config file for PathsTab
            def saveYaml(self):
                print sg_colors.green1 + "--- def browse_path(self): in class PathsTab(QMainWindow, ProjectPaths_layout.Ui_ProjectPathsLayout): inside CustomUIaction_Uililities.py ---" + sg_colors.endc
                data = {
                    'projects_root_path': self.projectRootPathField.text(),
                    'project_name': self.projectNameField.text(),

                }
                with open(yaml_Pathnames_Path, 'w') as export_hook_config:
                    export_hook_config.write(yaml.safe_dump(data))

        # Choose a set of export presets to be available in the Flame contextual menu.
        class ExportPresetsTab (QMainWindow, ExportPresets_layout.Ui_ExportPresetsLayout):
            def __init__(self, fileInfo, parent=None):
                super(ExportPresetsTab, self).__init__(parent)

                self.setupUi(self)
                self.pushButton_save.clicked.connect(self.saveYaml)  # When the button is pressed: saves the yaml config file
                self.browsePath.clicked.connect(self.browse_path)  # When the button is pressed: Execute browse_path function.
                self.browsePath02.clicked.connect(self.browse_path02)  # When the button is pressed: Execute browse_path function.
                self.browsePath03.clicked.connect(self.browse_path03)  # When the button is pressed: Execute browse_path function.
                self.browsePath04.clicked.connect(self.browse_path04)  # When the button is pressed: Execute browse_path function.
                self.browsePath05.clicked.connect(self.browse_path05)  # When the button is pressed: Execute browse_path function.

                # Default values. Read from existing Yaml config file. > Always start with actual config.
                # Maybe it should also have a reset to default option, reading from a seperate file?
                self.preset01PathField.setText(export_preset01_path)
                self.preset01NameField.setText(export_preset01_name)

                self.preset02PathField.setText(export_preset02_path)
                self.preset02NameField.setText(export_preset02_name)

                self.preset03PathField.setText(export_preset03_path)
                self.preset03NameField.setText(export_preset03_name)

                self.preset04PathField.setText(export_preset04_path)
                self.preset04NameField.setText(export_preset04_name)

                self.preset05PathField.setText(export_preset05_path)
                self.preset05NameField.setText(export_preset05_name)

            def browse_path(self):

                FileFullPath = QFileDialog.getOpenFileName(self, "browse")

                if FileFullPath:  # if user didn't pick a file don't continue
                    self.preset01PathField.setText(FileFullPath[0])

            def browse_path02(self):
                FileFullPath = QFileDialog.getOpenFileName(self, "browse")

                if FileFullPath:  # if user didn't pick a file don't continue
                    self.preset02PathField.setText(FileFullPath[0])

            def browse_path03(self):
                FileFullPath = QFileDialog.getOpenFileName(self, "browse")

                if FileFullPath:  # if user didn't pick a File don't continue
                    self.preset03PathField.setText(FileFullPath[0])

            def browse_path04(self):
                # self.preset03PathField.clear()  # In case there are any existing elements in the list
                FileFullPath = QFileDialog.getOpenFileName(self, "browse")

                if FileFullPath:  # if user didn't pick a directory don't continue
                    # self.projectNameField.saveLastOpenedDir(directory)
                    self.preset04PathField.setText(FileFullPath[0])

            def browse_path05(self):
                # self.preset03PathField.clear()  # In case there are any existing elements in the list
                FileFullPath = QFileDialog.getOpenFileName(self, "browse")

                if FileFullPath:  # if user didn't pick a directory don't continue
                    # self.projectNameField.saveLastOpenedDir(directory)
                    self.preset05PathField.setText(FileFullPath[0])

            def store_UIcontent(self):
                pass

            # YAML = Save the yaml config file for ExportPresetsTab
            def saveYaml(self):
                print sg_colors.green1 + "--- def saveYaml(self): in class ExportPresetsTab (QMainWindow, ExportPresets_layout.Ui_ExportPresetsLayout): inside CustomUIaction_Uililities.py ---" + sg_colors.endc

                data = {
                    'export_preset01': {
                        'path': self.preset01PathField.text(),
                        'name': self.preset01NameField.text(),
                    },
                    'export_preset02': {
                        'path': self.preset02PathField.text(),
                        'name': self.preset02NameField.text(),
                    },
                    'export_preset03': {
                        'path': self.preset03PathField.text(),
                        'name': self.preset03NameField.text(),
                    },
                    'export_preset04': {
                        'path': self.preset04PathField.text(),
                        'name': self.preset04NameField.text(),
                    },
                    'export_preset05': {
                        'path': self.preset05PathField.text(),
                        'name': self.preset05NameField.text(),
                    }
                }
                # with open('/opt/flame_dev/flame_hooks_sg/hooks_py_apps/utilities/ExportPresets_result.yaml', 'w') as Export_Presets_config:
                with open(yaml_export_presets, 'w') as Export_Presets_config:
                    Export_Presets_config.write(yaml.safe_dump(data))

        # Gives a set of names and emails that will conditionaly chosen (per export type, from 'export presets types') from within the custom export hook
        class StaffTab(QMainWindow, infoStaff_layout.Ui_infoStaffLayout):
            def __init__(self, fileInfo, parent=None):
                super(StaffTab, self).__init__(parent)

                self.setupUi(self)  # This is defined in infoStaff_layout.py file automatically. It sets up layout and widgets that are defined
                self.pushButton_save.clicked.connect(self.saveYaml)
                self.projectLeadName.setText("Stefan Lead")
                self.projectLeadEmail.setText("xenjee@gmail.com")
                self.producerName.setText("Stefan Prod")
                self.producerEmail.setText("stefan@pulsevfx.com")
                self.project2dLeadName.setPlaceholderText("2d Lead's Name")
                self.project2dLeadEmail.setPlaceholderText("2dLead@company.com")
                self.project3dLeadName.setPlaceholderText("3d Lead's Name")
                self.project3dLeadEmail.setPlaceholderText("3dLead@company.com")
                self.vfxTeamAlias.setPlaceholderText("Project: team's alias")
                self.vfxTeamEmail.setPlaceholderText("team@company.com")

            def store_UIcontent(self):
                pass

            # YAML = Save the yaml config file for StaffTab
            def saveYaml(self):
                print sg_colors.green1 + "--- def saveYaml(self): in class StaffTab(QMainWindow, infoStaff_layout.Ui_infoStaffLayout): inside CustomUIaction_Uililities.py ---" + sg_colors.endc

                data = {
                    'staff': {
                        'producer': {
                            'name': self.producerName.text(),
                            'email': self.producerEmail.text(),
                        },
                        'project_lead': {
                            'name': self.projectLeadName.text(),
                            'email': self.projectLeadEmail.text(),
                        },
                        'project_2d_lead': {
                            'name': self.project2dLeadName.text(),
                            'email': self.project2dLeadEmail.text(),
                        },
                        'project_3d_lead': {
                            'name': self.project3dLeadName.text(),
                            'email': self.project3dLeadEmail.text(),
                        },
                        'vfx_team': {
                            'name': self.vfxTeamAlias.text(),
                            'email': self.vfxTeamEmail.text(),
                        }
                    }

                }
                # with open('/opt/flame_dev/flame_hooks_sg/hooks_py_apps/utilities/InfoStaff_config_result.yaml', 'w') as InfoStaff_config:
                with open(yaml_Staff, 'w') as InfoStaff_config:
                    InfoStaff_config.write(yaml.safe_dump(data))

        tabdialog = TabDialog()
        tabdialog.show()
        # sys.exit(tabdialog.exec_()) #  doesn't seem to work from Flame.

        app.exec_()


# print 'End of CustomUIAction_Utilities:'
print sg_colors.orange1 + "--- End of CUA_config ---" + sg_colors.endc
print sg_colors.grey3 + '-' * 80 + sg_colors.endc
