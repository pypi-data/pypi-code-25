from flamepy_sg.scripts.customprints.ansi_colors import sg_colors
from flamepy_sg.modules import yaml
import os

absolute_path = os.path.realpath(__file__)
root_path = '/'.join(absolute_path.split('/')[0:-2])

yaml_Pathnames_Path = "{root}/scripts/project_config/ProjectPaths_config_result.yaml".format(root=root_path)
yaml_Staff = "{root}/scripts/project_config/InfoStaff_config_result.yaml".format(root=root_path)
yaml_export_presets = "{root}/scripts/project_config/ExportPresets_result.yaml".format(root=root_path)

print sg_colors.yellow1 + "absolute_path: " + sg_colors.grey3 + absolute_path + sg_colors.endc
print sg_colors.yellow1 + "root_path: " + sg_colors.grey3 + root_path + sg_colors.endc

print sg_colors.yellow1 + "yaml_Pathnames_Path: " + sg_colors.grey3 + yaml_Pathnames_Path + sg_colors.endc
print sg_colors.yellow1 + "yaml_Staff: " + sg_colors.grey3 + yaml_Staff + sg_colors.endc
print sg_colors.yellow1 + "yaml_export_presets: " + sg_colors.grey3 + yaml_export_presets + sg_colors.endc

print sg_colors.grey1 + '-' * 80 + sg_colors.endc
print sg_colors.blue2 + "export_hook_sg.py starting " + "- This goes just after imports : " + sg_colors.endc


##########################################################################
##########################################################################


with open(yaml_Pathnames_Path, 'r') as config1:
    cfg1 = yaml.load(config1)

with open(yaml_Staff, 'r') as config2:
    cfg2 = yaml.load(config2)

with open(yaml_export_presets, 'r') as config4:
    cfg4 = yaml.load(config4)

# PROJECT INFOS:
projects_root_path = cfg1["projects_root_path"]
project_name = cfg1["project_name"]
export_path = projects_root_path + '/' + project_name

# Project's STAFF: Names and emails
project_lead_name = cfg2["staff"]["project_lead"]["name"]
project_lead_email = cfg2["staff"]["project_lead"]["email"]
producer_name = cfg2["staff"]["producer"]["name"]
producer_email = cfg2["staff"]["producer"]["email"]


# Export Presets (path and name) from yaml config File (ExportPresets_result.yaml)
# later used to define which export presets are available from the contextual menu (custom exports)
# Also used to define profiles in 'getCustomExportProfiles' function.
export_preset01_name = cfg4["export_preset01"]["name"]
export_preset01_path = cfg4["export_preset01"]["path"]
export_preset02_name = cfg4["export_preset02"]["name"]
export_preset02_path = cfg4["export_preset02"]["path"]
export_preset03_name = cfg4["export_preset03"]["name"]
export_preset03_path = cfg4["export_preset03"]["path"]
export_preset04_name = cfg4["export_preset04"]["name"]
export_preset04_path = cfg4["export_preset04"]["path"]
export_preset05_name = cfg4["export_preset05"]["name"]
export_preset05_path = cfg4["export_preset05"]["path"]

# TEST YAMLs config input's input PRINTS to Flame shell.
print sg_colors.green1 + "PROJECT INFOS:" + sg_colors.grey3
print sg_colors.red2 + 'Network Projects root path: ' + sg_colors.yellow1 + projects_root_path + sg_colors.grey3
print sg_colors.red2 + 'Network Project name: ' + sg_colors.yellow1 + project_name + sg_colors.grey3
print sg_colors.red2 + 'Network Export path: ' + sg_colors.yellow1 + export_path + sg_colors.grey3
print ''
print sg_colors.green1 + "STAFF: " + sg_colors.grey3
print 'Project lead: ' + project_lead_name + ', ' + project_lead_email
print 'Producer: ' + producer_name + ', ' + producer_email
print ''
# USING ExportPresets_result.yaml created by 'ExportPresetsTab' class in CustomUIAction_utilities.py
print sg_colors.green1 + "EXPORT PRESETS:" + sg_colors.grey3
print export_preset01_name + ' - ' + export_preset01_path
print export_preset02_name + ' - ' + export_preset02_path
print export_preset03_name + ' - ' + export_preset03_path
print export_preset04_name + ' - ' + export_preset04_path
print export_preset05_name + ' - ' + export_preset05_path
print ''


# Initialize and Project change (literraly when switching projects) >

# Store the loaded project name
def appInitialized(projectName):
    global globFlameProject
    globFlameProject = projectName

# Do the same in projectChanged


def projectChanged(projectName):
    global globFlameProject
    globFlameProject = projectName

# END - Initialize and Project change


# --------------
# CREATE Global Object >
# There (settings) to store later pass infos from preExportAsset - info['resolvedPath'] and info['namePattern']

class export_settings(object):
    pass


settings = export_settings()

# END - CREATE Global Object
# --------------


# --------------
# Add Export Profiles in menu ... >

# Add some custom export profiles to the contextual menu
# 'exportType' will be called later and assiociated with an export preset.

# profiles is a dictionary
# Profile's values (see below) come from the variables earlier assigned to ExportPresets_result.yaml imported values.
# Ordering is a mystery so far

def getCustomExportProfiles(profiles):
    profiles[export_preset02_name] = {'exportType': export_preset02_name}
    profiles[export_preset01_name] = {'exportType': export_preset01_name}
    profiles[export_preset03_name] = {'exportType': export_preset03_name}
    profiles[export_preset04_name] = {'exportType': export_preset04_name}
    profiles[export_preset05_name] = {'exportType': export_preset05_name}


# END - Add Export Profiles
# --------------


# --------------
# preCustomExport >

def preCustomExport(info, userData):  # info and userData are dictionaries
    #global globFlameProject

    # print '-' * 50
    # print "From globFlameProject: Current Flame Project is: " + globFlameProject
    # print '-' * 50

    # Setup some default properties all exports will share
    # Override as desired in any given 'if' statement for a particular preset
    info['useTopVideoTrack'] = True
    info['isBackground'] = True
    info['exportBetweenMarks'] = False

    # Destination: root part of where the clip will be exported. the rest of the path is defined in the export preset itself.
    info['destinationPath'] = export_path + '/'
    print export_path + '/'

    # Make sure the destination directory exists and make it if not,
    if not os.path.exists(info['destinationPath']):
        os.makedirs(info['destinationPath'])

    # Figure out which custom export menu was called and chose the corresponding Export Preset: ExportPresets_result.yaml
    # the rest of the destination path in set in the export preset using tokens.
    if userData['exportType'] == export_preset02_name:
        info['presetPath'] = export_preset02_path

    elif userData['exportType'] == export_preset01_name:
        info['presetPath'] = export_preset01_path

    elif userData['exportType'] == export_preset03_name:
        info['presetPath'] = export_preset03_path

    elif userData['exportType'] == export_preset04_name:
        info['presetPath'] = export_preset04_path

    elif userData['exportType'] == export_preset05_name:
        info['presetPath'] = export_preset05_path

    print '-' * 50
    print "Selected Profile is " + userData['exportType']
    print "Destination Path: " + info['destinationPath']
    print '-' * 50

# END - preCustomExport
# --------------


# --------------
# SEQUENCE & ASSETS PUBLISH >
# Prints only, to show what they can pass.

def preExportSequence(info, userData):
    # PRINT # - from Tommy H
    print '-' * 50
    print 'Within preExportSequence ------- for k, v in info.iteritems(): print "%-24s: %s" % (k, v)'
    for k, v in info.iteritems():
        print "%-24s: %s" % (k, v)
    print '-' * 50


def preExportAsset(info, userData):
    # PRINT #
    print '-' * 50
    print 'Within preExportAsset ------- for k, v in info.iteritems(): print "%-24s: %s" % (k, v)'
    for k, v in info.iteritems():
        print "%-24s: %s" % (k, v)
    print '-' * 50

    settings.export_filePath = info['resolvedPath']
    settings.name_pattern = info['namePattern']


def postExportAsset(info, userData):
    pass


def postExportSequence(info, userData):
    pass

# END SEQUENCE & ASSETS PUBLISH
# --------------


# --------------
# postCustomExport: EMAILS >

def postCustomExport(info, userData):
    pass

    # ### ------ UNSECURED TEMP WAY (I beleive) - for internal dev only -------


print sg_colors.orange1 + "--- End of Export Hook ---" + sg_colors.grey3
print '-' * 80
print sg_colors.endc
