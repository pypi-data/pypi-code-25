import requests
import json
from ruamel import yaml
import os

from requests.auth import HTTPBasicAuth

from pathlib import Path

from .entry import JSONEntry

def yaml_rec_load(path, source, dest):
    ans = []
    for s in source:
        path2 = list(path)
        path2.append(s)
        if isinstance(source[s], str):
            ans.append({'path': path, 'id': s, 'source_string': source[s], 'translation': dest[s]})
        else:
            ans.extend(yaml_rec_load(path2, source[s], dest[s]))
    return ans

def yaml_rec_update(callback, source, old, new):
    ans = {}
    for i in new:
        o = ''
        s = ''
        n = new[i]
        try:
            s = source[i]
        except Exception:
            pass
        try:
            o = old[i]
        except Exception:
            pass
        if isinstance(n, str):
            if o == '':
                ans[i] = n
            elif n == '':
                ans[i] = o
            else:
                ans[i] = callback(s, o, n)
        else:
            ans[i] = yaml_rec_update(callback, s, o, n)
    return ans

class TransifexProject:
    def __init__(self, conf, name, lang, data = {}):
        self.uri = "https://www.transifex.com"
        self.conf = conf
        self.name = name
        self.lang = lang
        self.data = data
        self.basedir = ''
        self.contents = {}

    def open(self, basedir):
        self.basedir = basedir
        with open(self.basedir + '/project.info') as f:
            self.files = json.load(f)
        self.slugs = [x['slug'] for x in self.files]
        self.loadContent()

    def initialize(self, basedir):
        self.basedir = basedir
        self.updateFileList()
        with open(self.basedir + '/project.info', 'w') as f:
            f.write(json.dumps(self.files))
        for slug in self.slugs:
            self.getFile(slug)
        self.loadContent()

    def update(self, callback):
        self.updateFileList()
        for ff in self.files:
            slug = ff['slug']
            fname = self.filename(slug, False)
            sname = self.filename(slug, True)
            os.rename(fname, fname+'.old')
            self.getFile(slug)
            if ff['i18n_type'] == 'YML':
                with open(fname+'.old') as oldf:
                    with open(fname) as newf:
                        with open(sname) as sourcef:
                            old = yaml.safe_load(oldf)
                            new = yaml.safe_load(newf)
                            source = yaml.safe_load(sourcef)
                            realnew = yaml_rec_update(callback, source, old, new)
                            with open(fname, 'w') as f:
                                yaml.dump(realnew, f, Dumper=yaml.RoundTripDumper,
                                    allow_unicode=True)

    def updateFileList(self):
        self.files = []
        self.slugs = []
        ans = requests.get('https://api.transifex.com/organizations/'+
                self.data['organization']+'/projects/'+self.name+
                '/resources/?language_code='+self.lang,
                auth=HTTPBasicAuth('api', self.conf['token']))
        if ans.status_code == 200:
            l = json.loads(ans.text)
            self.slugs = [x['slug'] for x in l]
            self.files = l
    
    def loadContent(self):
        for ff in self.files:
            with open(self.filename(ff['slug'], True)) as f:
                with open(self.filename(ff['slug'], False)) as f2:
                    if ff['i18n_type'] == 'YML':
                        source = yaml.safe_load(f)
                        dest = yaml.safe_load(f2)
                        lang1 = list(source.keys())[0]
                        lang2 = list(dest.keys())[0]
                        self.contents[ff['slug']] = \
                            yaml_rec_load([lang2], source[lang1], dest[lang2])

    def getFile(self, slug):
        ans = requests.get('https://www.transifex.com/api/2/project/'+
                self.name+'/resource/'+slug+'/content',
                auth=HTTPBasicAuth('api', self.conf['token']))
        if ans.status_code == 200:
            with open(self.filename(slug, True), 'w') as f:
                f.write(json.loads(ans.text)['content'])

        ans = requests.get('https://www.transifex.com/api/2/project/'+self.name+
                '/resource/'+slug+'/translation/'+self.lang+'/?mode=translator',
                auth=HTTPBasicAuth('api', self.conf['token']))
        if ans.status_code == 200:
            with open(self.filename(slug, False), 'w') as f:
                f.write(json.loads(ans.text)['content'])
        else:
            print(ans.text)

    def filename(self, slug, is_source):
        ext = ''
        for ff in self.files:
            if ff['slug'] == slug:
                f = ff
                break
        if f['i18n_type'] == 'YML':
            ext = 'yml'
        return self.basedir + '/' + slug + ('.source' if is_source else '') + '.' + ext

    def send(self, interface):
        self.save()
        for ff in self.files:
            print('{} => {}'.format(ff['slug'], ff['i18n_type']))
            with open(self.filename(ff['slug'], False)) as f:
                content = f.read()
                sendcontent = {"content": content}
                ans = requests.put('https://www.transifex.com/api/2/project/'+
                        self.name+'/resource/'+ff['slug']+'/translation/'+self.lang+'/',
                        json=sendcontent, auth=HTTPBasicAuth('api', self.conf['token']))
                print(ans)
                print(ans.text)

    def save(self):
        for slug in self.slugs:
            data = {}
            for d in self.contents[slug]:
                path = d['path']
                curr = data
                for p in path:
                    if p in curr:
                        curr = curr[p]
                    else:
                        curr[p] = {}
                        curr = curr[p]
                curr[d['id']] = d['translation']
            with open(self.filename(slug, False), 'w') as f:
                yaml.dump(data, f, Dumper=yaml.RoundTripDumper, allow_unicode=True)

    def content(self):
        contents = {}
        for content in self.contents:
            contents[content] = [JSONEntry(x) for x in self.contents[content]]
        return contents
