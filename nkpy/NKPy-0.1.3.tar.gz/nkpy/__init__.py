import sys
import re
import nkpy.vars
import nkpy.utils

cmds = nkpy.vars.cmds


def run(a):
    global cmds

    a = a.replace('큰따옴표', '"')
    a = a.replace('작은따옴표', "'")

    cmds = nkpy.utils.sel_sort(cmds)

    for m in cmds.values():
        if a.find(m) != -1:
            n = a.find(m)
            raise SyntaxError('원래 있던 그런거는 쓰지 말아요. 이제 nkpy가 있으니깐요. {}에서 틀리셨습니다.'.format(a[n - 2] + a[n - 1] + a[n] + a[n + 1] + a[n + 2]))

    b = re.findall(r'\'(.+?)\'|"(.+?)"', a)
    for m in b:
        a = a.replace(m[0], '^')

    for n in cmds.keys():
        a = a.replace(n, cmds[n])

    for m in b:
        a = a.replace('^', m[0], 1)

    exec(a)


def rrun():
    if sys.argv is not None:
        try:
            with open(sys.argv[1], 'r') as v:
                a = v.read()
            run(a)
        except FileNotFoundError:
            a = ' '.join(sys.argv)
            b = a.find(sys.argv[1])
            a = a[b:]
            run(a)
        except IndexError:
            exit()
