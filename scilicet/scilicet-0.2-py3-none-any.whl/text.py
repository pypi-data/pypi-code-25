class Character:
    def __init__(self, in_str, italic=False):
        self.str = in_str
        self.italic = italic


class Text:
    def __init__(self, characters):
        if type(characters) == list:
            self.characters = characters
        elif type(characters) == Character:
            self.characters = [characters]

    def __add__(self, other):
        if type(other) == Text:
            self.characters += other.characters
        elif type(other) == Character:
            self.characters += [other]
        else:
            raise TypeError

    def to_srt(self):
        last_italic = False
        text = ""
        for current in self.characters:
            if current.italic & (not last_italic):
                last_italic = True
                text += "<i>" + current.str
            elif last_italic:
                last_italic = False
                text += "</i>" + current.str
            else:
                text += current.str

        italic_agnostics = [' ', '\n']
        for italic_agnostic in italic_agnostics:
            text.replace("</i>{}<i>".format(italic_agnostic), italic_agnostic)

        return text
