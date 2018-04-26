"""
Do all you can to keep Ardexa running
"""
from __future__ import print_function
import time
import subprocess

DEBUG = 1
TIMESTAMP = "%Y-%m-%dT%H:%M:%S%z"
BB_LOG_FILE = '/var/log/ardexa-black-box.log'
DNS_FILE = '/etc/resolv.conf'

# header = "# Datetime, CPU usage (%), MEM usage (%), SWAP usage (%), DISK usage (%), Ardexa Broker DNS ping, 8.8.8.8 IP ping, Gateway ping, NS Lookup broker.ardexa.com using 8.8.8.8, Ardexa running, Agent run state, Agent cloud connection, Agent message count, Agent loop count, Agent core loop state, Agent comm loop state, Agent core ticker, Agent comm ticker, Agent message cache\n"
def fix_dns(last):
    """If local DNS is broken, but 8.8.8.8 is working, update the system DNS"""
    if DEBUG:
        print("{} Ardexa agent DNS: local [{}], google [{}]".format(
            time.strftime(TIMESTAMP),
            last[5], last[8]))
    if last[5] == 'bad' and last[8] == 'good':
        with open(DNS_FILE, 'w') as dns_file:
            dns_file.write('nameserver 8.8.8.8\n')

        return True
    return False


def check_timers(second_last, last):
    """check that the tickers are incrementing"""
    if DEBUG:
        print("{} Ardexa agent ticker: core [{}, {}], comm [{}, {}]".format(
            time.strftime(TIMESTAMP),
            second_last[16], last[16],
            second_last[17], last[17]))
    if int(last[16]) == int(second_last[16]):
        return True

    if int(last[17]) == int(second_last[17]):
        return True

    return False


def check_connection(third_last, second_last, last):
    """compare cloud_connection vs blackbox internet"""
    if DEBUG:
        print("{} Ardexa agent connection: internet [{}, {}, {}], agent [{}]".format(
            time.strftime(TIMESTAMP),
            third_last[5], second_last[5], last[5],
            last[11]))
    if last[5] == 'good' and second_last[5] == 'good' and third_last[5] == 'good':
        # net has been good for 10 mins, check agent connection state
        if last[11] != 'True':
            return True
    return False


def check_msgs(third_last, last):
    """check msg and cache count: at least one must rise"""
        # agent hasn't budged in 10 minutes
    if DEBUG:
        print("{} Ardexa agent msgs: sent [{}, {}], cached [{}, {}]".format(
            time.strftime(TIMESTAMP),
            third_last[12], last[12],
            third_last[18], last[18]))
    return int(last[12]) == int(third_last[12]) and int(last[18]) == int(third_last[18])


def check_black_box():
    """Check the blackbox for network and agent state"""
    last = ''
    second_last = ''
    third_last = ''
    with open(BB_LOG_FILE) as bb_file:
        for line in bb_file:
            if line.startswith('#'):
                continue
            third_last = second_last
            second_last = last
            last = line.strip().split(',')

    if not last or not second_last or not third_last:
        print("Not enough data")
        return

    if fix_dns(last):
        return

    if (check_timers(second_last, last)
            or check_connection(third_last, second_last, last)
            or check_msgs(third_last, last)):
        restart_agent()
        return


def agent_enabled():
    """Check if agent service is enabled"""
    isenabled = subprocess.Popen(["systemctl", "is-enabled", "ardexa.service"],
                                 stdout=subprocess.PIPE)
    isenabled_output = isenabled.communicate()[0].strip()
    if DEBUG:
        print("{} Ardexa agent: current BOOT state: {}".format(
            time.strftime(TIMESTAMP), isenabled_output))

    return isenabled.returncode == 0 and isenabled_output == "enabled"


def agent_active():
    """Check if agent service is active"""
    isactive = subprocess.Popen(["systemctl", "is-active", "ardexa.service"],
                                stdout=subprocess.PIPE)
    isactive_output = isactive.communicate()[0].strip()
    if DEBUG:
        print("{} Ardexa agent: current RUN state: {}".format(
            time.strftime(TIMESTAMP), isactive_output))

    return isactive.returncode == 0 and isactive_output == "active"


def restart_agent():
    """Restart the agent service"""
    if DEBUG:
        print("{} Ardexa agent: calling START".format(
            time.strftime(TIMESTAMP)))

    return subprocess.call(["systemctl", "restart", "ardexa.service"]) == 0


def main():
    """Entry point"""
    if not agent_enabled():
        return

    if agent_active():
        check_black_box()
    else:
        restart_agent()


if __name__ == "__main__":
    main()
