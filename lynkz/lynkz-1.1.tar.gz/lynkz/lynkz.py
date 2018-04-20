# Written by Evan Pratten (ewpratten@gmail.com)
# Part of "lynkz" package
# https://github.com/Ewpratten/lynkz

from lxml import html
import requests

def delete(iurl, delkey):
    id = iurl[18:]
    a = requests.post(url = "https://new.lynkz.me/", data = {"action" : "new", "identifier": id})
    return 0


def shorten(iurl):
        r = requests.post(url = "https://new.lynkz.me/", data = {"action" : "new", "url": iurl, "content":"json"})
        d2 = html.fromstring(r.text)
        elemt = d2.xpath('//td/text()')
        elema = d2.xpath('//a/text()')
        data = r.text
        shorturl = elema[0]
        delkey = elemt[2]
        rdat = [shorturl, delkey]
        return rdat

