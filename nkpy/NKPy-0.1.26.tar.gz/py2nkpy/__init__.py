import sys
import re
import nkpy.vars
import nkpy.utils
from colorama import Fore

cmdds = nkpy.vars.cmds


def run(a):
    global cmds

    a = a.replace('"', '큰따옴표')
    a = a.replace("'", '작은따옴표')

    cmds = {}

    for b in cmdds.keys():
        cmds[cmdds[b]] = b

    cmds = nkpy.utils.sel_sort(cmds)

    k = re.findall(r'(from (?P<from>[a-zA-Z0-9가-힣!@#$%^*()\-_=+\\\|\[\]{};:\'",.<>\/?.]*) )?import (?P<import>[a-zA-Z0-9가-힣!@#$%^*()\-_=+\\\|\[\]{};:\'",.<>\/?.]*)( as (?P<as>[a-zA-Z0-9가-힣!@#$%^*()\-_=+\\\|\[\]{};:\'",.<>\/?.]*))?', a)
    k = list(k)
    v = []
    modules = []
    for m in k:
        for j in m:
            if not j == '':
                n = j.split('.')
                for c in n:
                    v.append(c)

    b = re.findall(r'작은따옴표작은따옴표작은따옴표(.+?)작은따옴표작은따옴표작은따옴표|큰따옴표큰따옴표큰따옴표(.+?)큰따옴표큰따옴표큰따옴표|작은따옴표(.+?)작은따옴표|큰따옴표(.+?)큰따옴표', a)
    for m in b:
        if m[0] != '':
            a = a.replace(m[0], '^', 1)
        if m[1] != '':
            a = a.replace(m[1], '^', 1)

    for n in cmds.keys():
        a = a.replace(n, cmds[n])

    for m in b:
        if m[0] != '':
            a = a.replace('^', m[0], 1)
        if m[1] != '':
            a = a.replace('^', m[1], 1)

    with open('{}.nkpy'.format(sys.argv[1].replace('.py', '')), 'w') as v:
        v.write(a)


def rrun():
    if sys.argv is not None:
        try:
            with open(sys.argv[1], 'r') as v:
                a = v.read()
            run(a)
        except IndexError:
            print(Fore.RED + "Enter the file name!")
            print(Fore.RESET)
            exit()


if __name__ == '__main__':
    rrun()
