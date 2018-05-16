#coding: utf8
from __future__ import absolute_import, print_function
from .server_status.status import get_system_status
import time

def print_status():
    status = get_system_status(includes_processes=False)
    print('cpu: %s' % status['cpu']['used'])
    print('mem: %s%%, %s used, %s total' % (status['mem']['percent'], status['mem']['used_for_human'], status['mem']['total_for_human']))
    print('disk: %s%%, %s used, %s total' % (status['disk']['percent'], status['disk']['used_for_human'], status['disk']['total_for_human']))
    print('io: %s%%, read %s/s, write %s/s' % (status['io']['util'], status['io']['read_speed_for_human'], status['io']['write_speed_for_human']))
    print('\n'*3)

def main():
    print_status()
    time.sleep(2)
    print_status()
    time.sleep(2)
    print_status()





if __name__ == '__main__':
    main()