# coding=utf-8

import netifaces as nf

print dir(nf)

def getRouter4G():
    gateway = nf.gateways()
    if nf.AF_INET in gateway:
        return gateway[nf.AF_INET][0][1] == '3g-4g'
    elif nf.AF_INET6 in gateway:
        return gateway[AF_INET6][0][1] == '3g-4g'
    else:
        return False
    pass
def getRouterWired():
    gateway = nf.gateways()
    if nf.AF_INET in gateway:
        return gateway[nf.AF_INET][0][1] == 'eth0.2'
    elif nf.AF_INET6 in gateway:
        return gateway[AF_INET6][0][1] == 'eth0.2'
    else:
        return False
    pass
def getRouterWireless():
    gateway = nf.gateways()
    if nf.AF_INET in gateway:
        return gateway[nf.AF_INET][0][1] == 'wlan0'
    elif nf.AF_INET6 in gateway:
        return gateway[AF_INET6][0][1] == 'wlan0'
    else:
        return False
    pass
def getRouterGatway():
    gateway = nf.gateways()
    if gateway['default'] == {}:
        return False
    else:
        return True
    pass

if __name__ == '__main__':
    print('test:')

