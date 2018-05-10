class Entry:
    def __init__(self, msgids, msgstrs, fuzzy, obsolete):
        self.msgids = msgids
        self.msgstrs = msgstrs
        self.fuzzy = fuzzy
        self.obsolete = obsolete

    def isTranslated(self):
        for msgstr in self.msgstrs:
            if msgstr == '':
                return False
        return True

    def isFuzzy(self):
        return self.fuzzy

    def isObsolete(self):
        return self.obsolete

    def update(self, index, content):
        self.msgstrs[index] = content

class POEntry(Entry):
    def __init__(self, entry):
        msgids = [entry.msgid]
        msgstrs = [entry.msgstr]
        if 0 in entry.msgstr_plural:
            msgstrs = []
            for msgstr in entry.msgstr_plural:
                msgstrs.append(entry.msgstr_plural[msgstr])
            msgids = [entry.msgid, entry.msgid_plural]
        Entry.__init__(self, msgids, msgstrs, "fuzzy" in entry.flags, entry.obsolete)
        self.entry = entry

    def update(self, index, content):
        Entry.update(self, index, content)
        self.fuzzy = False
        self.entry.flags = [x for x in self.entry.flags if x != 'fuzzy']
        if 0 in self.entry.msgstr_plural:
            self.entry.msgstr_plural[index] = content
        else:
            self.entry.msgstr = content

class JSONEntry(Entry):
    def __init__(self, entry):
        Entry.__init__(self, [entry['source_string']], [entry['translation']], False, False)
        self.entry = entry

    def update(self, index, content):
        Entry.update(self, index, content)
        self.entry['translation'] = content

class YAMLEntry(Entry):
    def __init__(self, entry):
        self.key = list(entry.keys())[0]
        Entry.__init__(self, self.key, entry[self.key], False, False)
        self.entry = entry

    def update(self, index, content):
        Entry.update(self, index, content)
        self.entry[self.key] = content
