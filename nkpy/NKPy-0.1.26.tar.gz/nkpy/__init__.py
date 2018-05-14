import sys
import re
import nkpy.vars
import nkpy.utils
import glob
import atexit
import os

cmds = nkpy.vars.cmds


def run(a, excu=True):
    global cmds

    a = a.replace('큰따옴표', '"')
    a = a.replace('작은따옴표', "'")

    cmds = nkpy.utils.sel_sort(cmds)

    k = re.findall(r'(로부터 (?P<from>[a-zA-Z0-9가-힣!@#$%^*()\-_=+\\\|\[\]{};:\'",.<>\/?.]*) )?가져와 (?P<import>[a-zA-Z0-9가-힣!@#$%^*()\-_=+\\\|\[\]{};:\'",.<>\/?.]*)( 으로 (?P<as>[a-zA-Z0-9가-힣!@#$%^*()\-_=+\\\|\[\]{};:\'",.<>\/?.]*))?', a)
    k = list(k)
    v = []
    modules = []
    for m in k:
        for j in m:
            if not j == '':
                n = j.split('.')
                for c in n:
                    v.append(c)

    for m in v:
        j = glob.glob('{}.nkpy'.format(m), recursive=True)
        for x in j:
            modules.append(x)
            with open('{}'.format(x), 'r') as b:
                with open('{}'.format(x.replace('.nkpy', '.py')), 'w') as h:
                    write_some = run(b.read(), excu=False)
                    h.write(write_some)

    b = re.findall(r'\'\'\'(.+?)\'\'\'|"""(.+?)"""|\'(.+?)\'|"(.+?)"', a)
    for m in b:
        if m[0] != '':
            a = a.replace(m[0], '^', 1)
        if m[1] != '':
            a = a.replace(m[1], '^', 1)

    for m in cmds.values():
        bol = False
        if a.find(m) != -1:
            n = a.find(m)
            for c in v:
                h = len(c)
                y = a.find(c)
                for u in range(h):
                    if a[y + u] == a[n]:
                        bol = True
            if not bol:
                raise SyntaxError('원래 있던 그런거는 쓰지 말아요. 이제 nkpy가 있으니깐요. {}에서 틀리셨습니다.'.format(a[n - 2] + a[n - 1] + a[n] + a[n + 1] + a[n + 2]))

    for n in cmds.keys():
        a = a.replace(n, cmds[n])

    for m in b:
        if m[0] != '':
            a = a.replace('^', m[0], 1)
        if m[1] != '':
            a = a.replace('^', m[1], 1)

    a = "import sys\nsys.path.insert(0, '{}')\n\n".format(os.getcwd()) + a

    if excu:
        try:
            exec(a)
            return modules
        except KeyboardInterrupt:
            return modules
    else:
        return a


def on_exit(v):
    try:
        for a in v:
            os.remove(a.replace('.nkpy', '.py'))
    except NameError:
        pass


def rrun():
    if sys.argv is not None:
        try:
            with open(sys.argv[1], 'r') as v:
                a = v.read()
            b = run(a)
            atexit.register(on_exit, b)
        except FileNotFoundError:
            a = ' '.join(sys.argv)
            b = a.find(sys.argv[1])
            a = a[b:]
            c = run(a)
            atexit.register(on_exit, c)
        except IndexError:
            exit()


if __name__ == '__main__':
    rrun()
