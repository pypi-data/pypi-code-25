
import zipfile 
import lxml 
import lxml.etree
import functools

class ODSDocument(object):
    
    def __init__(self, path):
        archive = zipfile.ZipFile(path, 'r')
        self.contents = archive.read("content.xml")
        self.tree = lxml.etree.fromstring(self.contents)
        
        rows = [[([c] * int(_get_attr(c, "number-columns-repeated", 1)))
            for c in r.iter() if c.tag.endswith("cell")] for r in self.tree.iter() if r.tag.endswith("row")]
        rows = [functools.reduce(lambda x,y: x+y, r, []) for r in rows]
        self.rows = [[ODSCell.fromxml(c) for c in r] for r in rows]


class ODSCell(object):
    
    def __init__(self, value="", number_rows_spanned=1):
        self.value = value 
        self.number_rows_spanned = number_rows_spanned

    def fromxml(xml):
        return ODSCell(value="".join([e.text for e in xml.iter() if e.text != None]), number_rows_spanned = int(_get_attr(xml, "number-rows-spanned", 1)))

    def __str__(self):
        return self.value
    
def _get_attr(e, attr, default):
    a = [v for k,v in e.attrib.items() if k.endswith(attr)]
    if a == []: 
        return default
    else:
        return a[0]
