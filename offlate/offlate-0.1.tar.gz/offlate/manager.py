from pathlib import Path
from .systems.tp import TPProject
from .systems.transifex import TransifexProject

import json
import os

class ProjectSettings:
    def __init__(self, confdir):
        self.confdir = confdir
        self.reload()

    def write(self):
        with open(self.confdir + '/conf.json', 'w') as f:
            f.write(json.dumps(self.conf))

    def reload(self):
        try:
            with open(self.confdir + '/conf.json') as f:
                self.conf = json.load(f)
        except Exception:
            with open(self.confdir + '/conf.json', 'w') as f:
                f.write(json.dumps({}))

class ProjectManager:
    def __init__(self):
        self.projects = []
        self.project_list = dict()
        home = str(Path.home())
        self.basedir = home + '/.local/share/offlate'
        self.confdir = home + '/.config/offlate'
        Path(self.basedir).mkdir(parents=True, exist_ok=True)
        Path(self.confdir).mkdir(parents=True, exist_ok=True)
        self.settings = ProjectSettings(self.confdir)
        try:
            with open(self.basedir + '/projects.json') as f:
                self.projects = json.load(f)
                for p in self.projects:
                    if p['system'] == 0:
                        if not "TP" in self.settings.conf:
                            self.settings.conf["TP"] = {}
                        self.project_list[p['name']] = \
                            TPProject(self.settings.conf["TP"], p['name'], p['lang'], p['info'])
                        self.project_list[p['name']].open(self.basedir+'/'+p['name'])
                    if p['system'] == 1:
                        if not "Transifex" in self.settings.conf:
                            self.settings.conf['Transifex'] = {}
                        self.project_list[p['name']] = \
                            TransifexProject(self.settings.conf['Transifex'], p['name'], p['lang'], p['info'])
                        self.project_list[p['name']].open(self.basedir+'/'+p['name'])
        except Exception as e:
            print(e)
            with open(self.basedir + '/projects.json', 'w') as f:
                f.write(json.dumps([]))

    def createProject(self, name, lang, system, data):
        projectpath = self.basedir + '/' + name
        Path(projectpath).mkdir(parents=True)
        if system == 0: #TP
            if not "TP" in self.settings.conf:
                self.settings.conf["TP"] = {}
            proj = TPProject(self.settings.conf["TP"], name, lang)
            proj.initialize(projectpath)
            self.project_list[name] = proj
            self.projects.append({"name": name, "lang": lang, "system": system,
                    "info": {"version": proj.version}})
        if system == 1: #Transifex
            if not 'Transifex' in self.settings.conf:
                self.settings.conf['Transifex'] = {}
            proj = TransifexProject(self.settings.conf['Transifex'], name, lang, data)
            proj.initialize(projectpath)
            self.project_list[name] = proj
            self.projects.append({"name": name, "lang": lang, "system": system,
                    "info": data})
        self.writeProjects()

    def writeProjects(self):
        with open(self.basedir + '/projects.json', 'w') as f:
            f.write(json.dumps(self.projects))

    def listProjects(self):
        return self.projects

    def getProject(self, name):
        return self.project_list[name]

    def updateSettings(self, data=None):
        if data == None:
            self.settings.conf = data
            self.settings.update()
        else:
            self.settings.write()

    def getConf(self):
        return self.settings.conf
