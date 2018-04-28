#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests

headers = {'Token': '53a308a3-93ad-11e7-9876-28cfe91a6a05'}

if __name__ == '__main__':
    try:
        r = requests.get('http://qp.alta.elenet.me/api/stability/report', headers=headers)
        if r.ok:
            for d in r.json()['data']:
                if d['device'].strip() == '':
                    print str(d['id']) + '===' + d['device']
                    requests.delete('http://qp.alta.elenet.me/api/stability/report/{}'.format(d['id']), headers=headers)
    except requests.RequestException:
        pass
