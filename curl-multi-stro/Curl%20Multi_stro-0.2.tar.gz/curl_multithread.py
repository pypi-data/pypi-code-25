#!/usr/bin/env python

'''
        Created by:     Matthew Strozyk
        Date:           September 2017
'''


import threading, sys, json, os, subprocess, argparse, webbrowser, random, string
from datetime import datetime, date
from threading import Thread

try:
    import requests
except:
    print "You need to install requests."
    print "For Mac run: sudo easy_install -U requests"
    print "For Linux run: pip install requests"
    exit()

# Global Variables

# Number of times to run curl command on each host in a vip
ITERATIONS = 1

# Name of the page that goes in the curl request: "host: <PAGENAME>"
PAGENAME = None

# Used to see if this is a mobile curl check
MOBILEOPTION = False

# Number of threads that will run = ITERATIONS x NUM HOSTS IN VIP
TOTALTHREADS = 0

# Number of curl command threads that have exited
NUMEXITED = 0

# Name of the vip that was inputted or found
VIP = ""

# Base url for interacting with API
# <removed for security reasons>

# Element of the inputted page that should be curled against
#    Example: www.yahoo.com/this-is-the-element
ELEMENT = ""

# Holds all the CurlHost objects
CURL_HOSTS = []

# Default response time to look for in returned curl output
RESPONSE_TIME_THRESHOLD = 10

# Keeps track of it iterative curl command has already been run
RAN_PREVIOUSLY = False

# Tells the program if this is to be run interactively or not
HELPER_MODE = True

# Lock used to update the number of threads that have exited
EXIT_COUNT_LOCK = threading.Lock()

class Colors:
    '''
    Basic class used for coloring output written to terminal/file
    '''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    ERROR = '\033[91m'
    ENDC = '\033[0m'
    WARNING = '\033[93m'
    BOLD = '\033[1m'
    TEST = '\033[42m'
    BACKRED = '\033[41m'
    WHITETEXT = '\033[37m'
    PURPLE = '\033[35m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'

###########################################################################
#
# All Getch classes are used for accepting single character input
#   - This is used in the y/n questions
#
###########################################################################

class _Getch:
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()

class CurlHost:
    '''
    Used to keep track of the host in the vip as well as it's curl output

    More Info:
        - A CurlHost is a SINGLE HOST in a vip that will have 1-n curl commands
        ran against it
        - This also is the master thread as it will spawn off 1-n threads to execute
          all the curl commands

    Constructor Params:
        hostname - the name of the host that this is representing

    Other Variables:
        results - stores the output of each curl command for this host
        fourHunds - string of all 4xx curl output found
        fiveHunds - string of all 5xx curl output found
        fourLock - lock used for synchronization while updating fourHunds
        fiveLock - lock used for synchronization while updating fiveHunds
    '''
    def __init__(self, hostname, isVip):

        self.hostname = hostname
        self.results = []
        self.fourHunds = ""
        self.fiveHunds = ""
        self.fourLock = threading.Lock()
        self.fiveLock = threading.Lock()
        self.myLock = threading.Lock()
        self.numLock = threading.Lock()
        self.uniqueNum = 1
        self.threads = []
        self.uniqueString = randomword(4)
        self.isVip = isVip
        self.vipReturns_Errors = []
        self.vipReturnTime_Errors = []
        self.problemHosts = {}

    def append_result(self,result):
        '''
        Adds curl information to the total_output variable which is eventually
        outputted to the user
        '''
        self.myLock.acquire()
        self.results.append(result)
        self.myLock.release()

    def colorHTTP(self, line):
        '''
        This is used to color the hosts in the Via line of curl output
        '''

        # Split by whitespace
        l = line.split()

        # Change Color
        for i in range(0,len(l)):
            if "http" in l[i]:
                l[i+1] = Colors.OKBLUE+l[i+1]+Colors.ENDC

        return ' '.join(l)


    def colorOutput(self, cout):
        '''
        Colors the output of the curl command to make it easier to see

        *****
        MUST BE IN THIS FORMAT:
        Return Code = 200 Connect= 0.029141s App Time = 0.099375s Total Time = 0.499127s
        *****
        '''

        # cout[3][0] - The return code number received from curl output
        #   Example: Return Code = 301
        #      - cout[3] is "301"
        #      - cout[3][0] would be "3"

        if cout[3][0] is "0":
            cout[3] = Colors.WARNING+cout[3]+Colors.ENDC
        elif cout[3][0] is "2":
            cout[3] = Colors.OKBLUE+cout[3]+Colors.ENDC
        elif cout[3][0] is "3":
            cout[0] = Colors.BACKRED+Colors.WHITETEXT+cout[0]
            cout[len(cout)-1] = cout[len(cout)-1]+Colors.ENDC
        elif cout[3][0] is "4":
            cout[0] = Colors.BACKRED+cout[0]
            cout[len(cout)-1] = cout[len(cout)-1]+Colors.ENDC
            self.updateFourHunds(' '.join(cout))
        elif cout[3][0] is "5":
            cout[0] = Colors.BACKRED+cout[0]
            cout[len(cout)-1] = cout[len(cout)-1]+Colors.ENDC
            self.updateFiveHunds(' '.join(cout))

        return cout

    def findProblemHosts(self, line):
        '''
        Finds all the hosts in the line that are related to the problem.
        This is based on the "Via" line in curl output

        '''

        # Split by whitespace
        l = line.split()

        for i in range(0,len(l)):
            if "http" in l[i]:
                host = l[i+1]
                if host in self.problemHosts:
                    self.problemHosts[host] += 1
                else:
                    self.problemHosts[host] = 1





    def reset_results(self):
        '''
        Resets all results within this curlHost
           - This is used if the iterative curl command is ran again
        '''
        self.fourHunds = ""
        self.fiveHunds = ""
        self.results = []
        self.vipReturns_Errors = []
        self.vipReturnTime_Errors = []
        self.problemHosts = {}

    def run(self):
        '''
        This spawns off all the curl commands for this curlhost.
        After doing so it updates the data that it gathered

        '''
        for _ in range(ITERATIONS):

            if self.isVip is True:
                tmp_curlthread = Thread(target = self.runVipThread, args = (self.uniqueNum, ))
            else:
                # Assign thread function
                tmp_curlthread = Thread(target = self.runSingleCurlThread, args = (self.uniqueNum, ))

            # Increment unique number after assigning it
            self.uniqueNum += 1

            # Start Threads
            tmp_curlthread.start()

            # Need to keep track of threads
            self.threads.append(tmp_curlthread)

        # Wait for all threads to exit
        for i in self.threads:
            i.join()

    def runSingleCurlThread(self, id):
        '''
        This runs a single curl command on the host for this CurlHost

        @params
          identifier - unique NUMBER that is assigned for splunk purposes
          specialKey - unique String assigned for splunk purposes
        '''

        identifier = id
        specialKey = self.uniqueString

        # Run curl command
        if MOBILEOPTION is False:
            proc = subprocess.Popen(["curl -so /dev/null -w 'Return Code = %{http_code} Connect= %{time_connect}s App Time = %{time_appconnect}s Total Time = %{time_total}s'  -kLH \"host: "+PAGENAME+"\" http://"+self.hostname+"/"+ELEMENT+"/?"+specialKey+"="+str(identifier)+"; printf \" Exit code: \"$?\"\n\" "], stdout=subprocess.PIPE, shell=True)
        else:
            proc = subprocess.Popen(["curl -D - -so /dev/null -A \"Mozilla/5.0 (iPhone; CPU iPhone OS 10_0 like Mac OS X) AppleWebKit/602.1.38 (KHTML, like Gecko) Version/10.0 Mobile/14A5297c Safari/602.1\" -w 'Return Code = %{http_code} Connect= %{time_connect}s App Time = %{time_appconnect}s Total Time = %{time_total}s' -H \"host: "+PAGENAME+"\" -k https://"+self.hostname+"/"+ELEMENT+"/?"+specialKey+"="+str(identifier)+"; printf \" Exit code: \"$?\"\n\" "], stdout=subprocess.PIPE, shell=True)

        # Get curl output
        (out, err) = proc.communicate()

        # Parse output and detect errors
        curl_out = out.split()

        # Get the output the way we want it
        cout = self.colorOutput(curl_out)

        # Append the result
        self.append_result(["    "+' '.join(curl_out), identifier, specialKey])

        # Update the output percent/numExited
        updatePercent()

    def runVipThread(self, id):
        '''
        This runs a single curl command on the host for this CurlHost.
            More specifically this is for only hitting a vip and not
            a host in the vip

        @params
          identifier - unique NUMBER that is assigned for splunk purposes
          specialKey - unique String assigned for splunk purposes
        '''

        identifier = id
        specialKey = self.uniqueString
        proc = subprocess.Popen(["curl -sD - -o /dev/null -w '\nStart of data: \nReturn code = %{http_code}\nConnect_Time= %{time_connect}s\nDNS Time = %{time_namelookup}s\nApp_Time = %{time_appconnect}s\ntime_redirect = %{time_redirect}s\ntime_pretransfer = %{time_pretransfer}s\ntime_starttransfer = %{time_starttransfer}s\n\nTotal Time = %{time_total}s\n\n'  -kLH \"Host: "+PAGENAME+"\" https://"+self.hostname+"/?"+specialKey+"="+str(identifier)+" ; printf \" Exit code: \"$?\"\n\" "], stdout=subprocess.PIPE, shell=True)

        # Get curl output
        (out, err) = proc.communicate()


        # Split by lines
        cout = out.splitlines()

        output = ""
        # Return Code = 200 Connect= 0.029141s App Time = 0.099375s Total Time = 0.499127s

        # Set Via line as default
        via = "No Via was found."

        # Parse the lines and assign variables
        for line in cout:
            if "Return code =" in line or "Total Time =" in line or "Connect_Time" in line or "App_Time" in line:

                if "Return code =" in line:
                    # Check if not a 200
                    if "200" not in line.split()[3]:
                        # Find 'Via' line
                        for l in reversed(cout):
                            if "Via:" in l:
                                via = l
                                break

                        self.findProblemHosts(l)

                        # Add to array in format:
                        # [Return code, vip line that supplied this]
                        self.vipReturns_Errors.append([line.split()[3], self.colorHTTP(via)])

                if "Total Time =" in line:
                    # Parse to get the response time
                    rTime = int((line.split()[3]).split('.')[0])
                    # Check if it is over threshold
                    if rTime >= RESPONSE_TIME_THRESHOLD:
                        # Find 'Via' line
                        for l in reversed(cout):
                            if "Via:" in l:
                                via = l
                                break

                        self.findProblemHosts(l)

                        # Add to array in format:
                        # [Total Time, vip line that supplied this]
                        self.vipReturnTime_Errors.append([line.split()[3], self.colorHTTP(via)])

                # Add found line to output
                output = ' '.join([output,line])

        cout = self.colorOutput(output.split())

        # Add result to variable
        self.append_result(["    "+' '.join(cout), identifier, specialKey])

        # Update the output percent/numExited
        updatePercent()


    def set_result(self,result):
        '''
        Sets the full results as an array:
        Format:
            results[i][0] - Single Curl Command output
            results[i][1] - Number/Identifier used for splunk (1-n)
            results[i][2] - Random string used for splunk query (unique to each host hit)

        @params
            results - array of information formatted as shown above

        '''
        self.results = result

    def updateFiveHunds(self, fiveHunds):
        '''
        Updates the five hundred results for this host

        @params
            fiveHunds - Single curl command output that has a 5xx in it
        '''
        self.fiveLock.acquire()
        self.fiveHunds += fiveHunds + "\n"
        self.fiveLock.release()

    def updateFourHunds(self, fourHunds):
        '''
        Updates the four hundred results for this host

        @params
            fourHunds - Single curl command output that has a 4xx in it
        '''
        self.fourLock.acquire()
        self.fourHunds += fourHunds + "\n"
        self.fourLock.release()

#-----------------------------------------------------
# End Of Classes
#-----------------------------------------------------

def curl_return_codes_MAIN():
    '''
    This is the starting point of the return codes option in this program.

    @params
        HELPER_MODE - True if this is being run as an interactive program
                     False if ran with command line arguments
    '''

    global RAN_PREVIOUSLY
    global ITERATIONS
    global RESPONSE_TIME_THRESHOLD
    global TOTALTHREADS
    global HELPER_MODE

    # Used for performance metrics - Timing
    start = datetime.now()

    # check if this is a ycpi vip
    if "ycpi" in VIP:
        findVipOrigin()

    print "The origin vip found is: "+Colors.OKBLUE+VIP+Colors.ENDC

    # Check if this is the second time running the curl commands
    if not RAN_PREVIOUSLY:
        # See if you can find in Libra
        if get_host_list() is False:
            print Colors.ERROR+"Unable to find hosts in that vip through Libra."+Colors.ENDC
            print "Try running a basic curl check with option 1."
            return

        # Set RAN_PREVIOUSLY
        RAN_PREVIOUSLY = True

    # Prompt user for iterations
    setNumIterations()

    # Prompt user for new response time threshold
    setResponseTime()

    # Prints out all the pre-curl info to the user
    printInfoToUser()

    # Spawn off curl threads to gather the results
    run_curl_threads()

    # Print results out to user
    print_curl_results()

    # Print curl error code page link
    print "\n\nExit Code Page: "+Colors.OKBLUE+"https://curl.haxx.se/libcurl/c/libcurl-errors.html\n"+Colors.ENDC

    # Find any OTRs and print them
    printOverThresholdReturns()

    # Get end time reading for performance
    end = datetime.now()

    print "Total Time: "+str(end - start)

    # See if ran with args or not
    # HELPER_MODE is True if ran with NO args

    if HELPER_MODE is True:
        save_to_file_option()

    if HELPER_MODE is False:
        #See if save option is on
        if save_filename is not None:
            write_to_file(save_filename)
        exit()

def display_menu_get_input():
    '''
    Displays the menu option to the user and gets the desired command to run.
    Note that this will not be called if the user has command line arguments,
    making HELPER_MODE equal true.
    '''

    global ITERATIONS
    global RESPONSE_TIME_THRESHOLD
    global CURL_HOSTS

    # Print out the menu to the user
    while True:
        print """
Menu:
    1 - Basic Curl Command
    2 - Return Codes
    3 - Troubleshoot Vip
    4 - Splunk (Frontpage Only)
    q - Quit
            """

        # Get user input
        while True:
            inpt = raw_input("Selection: ")
            if inpt is "1":

                run_basic_curl()
                break

            elif inpt is "2":

                print("Not supported in this program.")
                break

                # Put everything back in to pre-run form
                reset_variables()

                # Run main curl function
                curl_return_codes_MAIN()
                break
            elif inpt is "3":

                # Put everything back in to pre-run form
                reset_variables()

                # Reset curl host array
                CURL_HOSTS = []

                # Iterate over vip
                hitTheVip()
                break

            elif inpt is "4":

                # Assemble splunkLink
                splunkLink = "https://splunk2.media.yahoo.com/splunk/en-US/app/search/search?earliest=-12h&latest=now&q=search%20index%3D*%20sourcetype%3Dats_mon_log%20%22"+PAGENAME+"%22%20%22dynatrace%3D1%22%20status%3D*&display.page.search.mode=smart&dispatch.sample_ratio=1&sid=1505317908.276702_68D7BEEA-F625-4BCC-B687-42A385E2B4FB"

                # Output splunklink
                print "Splunk link: "+splunkLink

                # Open splunklink in browser
                webbrowser.open(splunkLink)
                break

            elif inpt is "q":
                exit()
            else:
                continue

def findOverThresholdReturns():
    '''
    Parse the output and see if any responses are over the threshold set by default/user

    @returns
        overThresholdReturns - Array with all the overthreshold returned output
    '''

    global CURL_HOSTS
    global RESPONSE_TIME_THRESHOLD

    overThresholdReturns = []

    for curlhost in CURL_HOSTS:
        for result in curlhost.results:

            # This gives you just the number in the response time
            # Example response:
            # Return Code = 200 Connect= 0.000028s App Time = 0.000028s Total Time = 22.597929s Exit code: 0
            if int((result[0].split('Total Time = ')[1]).split('.')[0]) >= RESPONSE_TIME_THRESHOLD:
                rLine = result[0].split()

                # Make Total Time red
                for i in range(0, len(rLine)):
                    if rLine[i] is "Total":
                        rLine[i+3] = Colors.ERROR+rLine[i+3]+Colors.ENDC
                        break

                tmp = []
                tmp.append(curlhost.hostname)
                tmp.append(' '.join(rLine))
                tmp.append(result[1])
                tmp.append(result[2])
                overThresholdReturns.append(tmp)

    return overThresholdReturns

def findVipOrigin():
    '''
    Figures out what the actual vip that serves the YCPI is

    Explanation:
        Sometimes you will find that the IP you get from gomez is actually
        a ycpi host and not a vip. This means that there isn't any hosts
        to curl from that ycpi, but rather is serves as a caching host to
        quickly deliver results as requested. This caching host, however,
        gets it's content from a vip and in order to find that vip, you have
        to do an origin lookup.
    '''

    global VIP, PAGENAME

    print "YCPI host recognized. Finding the origin vip..."

    foundVip = ""

    # Run the origin lookup curl command
    basic_curl = subprocess.Popen(["curl -sD - -kLH \"Host: "+PAGENAME+"\" https://"+VIP+"/ -o /dev/null "], stdout=subprocess.PIPE, shell=True)
    (out, err) = basic_curl.communicate()

    # Find out what the origin vip is by parsing the output
    for line in reversed(out.splitlines()):
        if "Via:" in line:
            foundVip = line.split()[2]
            break

    # Check to see if it successfully found the origin vip
    if foundVip is "":
        print "Unable to find the vip for that YCPI host... OOPS! Exiting..."
        exit()

    # Construct the libra seach url
    # <removed for security reasons>

    # Try to get the vip information from libra
    try:
        r = requests.get(libraSearch).json()
    except:
        print "Libra may be down. Exiting..."
        exit()

    # Assign the vip name, exit if not found
    try:
        for i in r['members']:
            VIP = i['vip']
    except:
        print "Unable to find vip members through libra. Exiting..."
        exit()

def fixIfIP(vipInput):
    '''
    Checks if the input is an IP. If it is, it translates it to the vip name via DNS lookup

    @params
        vipInput - string to check if IP or not

    @returns
        FQDN of the IP address
    '''

    # First see if this is an IP Address or not

    # IPV4
    if '.' in vipInput:
        for i in vipInput.split('.'):
            if not i.isdigit():
                return vipInput
    # IPV6
    elif ':' in vipInput:
        pass
    else:
        return vipInput

    # Need to do nslookup now
    tmpVip = ""

    # Perform nslookup
    process = subprocess.Popen(["nslookup", vipInput], stdout=subprocess.PIPE)
    nsout = process.communicate()[0].split('\n')

    # Get the name outputted from the nslookup
    for i in nsout:
        if "name" in i:
            tmpVip = i.split(" = ")[1]
            tmpVip = tmpVip[:-1]

    # Check if we actually found a name
    if tmpVip is "":
        print "Error while trying to find parse IP. Exiting..."
        exit()
    else:
        return tmpVip

def get_curl_info():
    '''
    Prompts the user to get the information for the vip to curl on

    Sets global variables:
        - URL
        - VIP
        - PAGENAME
        - ITERATIONS
    '''

    global VIP
    global PAGENAME
    global ITERATIONS
    global LIBRAURL
    global MOBILEOPTION

    while True:

        # Get the full url from user
        fullUrl = raw_input("Complete URL: ")

        # Get the vipname from the user
        tmpVip = raw_input("Vip Name/IP Address: ")

        # Find out if it's for a mobile check or not
        tmpMobile = getYesOrNo("For a mobile check?(y/n):")

        # Output the user's inputted data back to them for confirmation
        print "\n-------------------------------------"
        print "Complete URL: "+Colors.OKBLUE+fullUrl+Colors.ENDC+"\nVip Name/IP Address: "+Colors.OKBLUE+tmpVip+Colors.ENDC
        print "Mobile Check: ",
        if tmpMobile is "y":
            print Colors.OKGREEN+"Yes"+Colors.ENDC
        else:
            print Colors.ERROR+"No"+Colors.ENDC
        print "-------------------------------------"

        while True:

            # Ask for confirmation from the user
            selection = getYesOrNo("\nIs this information correct? ("+Colors.OKGREEN+"y"+Colors.ENDC+"/"+Colors.ERROR+"n"+Colors.ENDC+"): ")

            if selection is "y":

                # Check if IP is inputted
                tmpVip = fixIfIP(tmpVip)

                # Set the variables
                parse_url(fullUrl,False)
                parse_url(tmpVip,True)

                if tmpMobile is "y":
                    mobileOption = True
                return
            elif selection is "n":
                print ""
                break

def get_host_list():
    '''
    Gets all the hosts in the vip by requesting it from the Libra API
    '''

    global CURL_HOSTS
    global LIBRAURL
    global VIP

    hosts = []

    # Used to see if origin vip already looked up or not
    firstTry = True

    print "Requested url is: "+LIBRAURL+VIP

    while True:

        # Try to get the vip info from Libra
        try:
            req = requests.get(LIBRAURL+VIP).json()
        except:
            print "Could not connect to "+Colors.OKBLUE+LIBRAURL+VIP+Colors.ENDC+". Max retries exceeded."
            exit()

        # See if Libra found the vip or not
        try:
            if req['errorcode'] == 404:
                if firstTry is True:
                    # See if there is an origin vip
                    # If it gets past here without exiting, it found a VIP
                    findVipOrigin()
                    firstTry = False
                    continue
                else:
                    print "Error in Libra response."
                    return False
        except:
            # If it's found in Libra, exit while loop
            break

    # Get all the hosts in the vip and create CurlHost objects for them
    try:
        for vip in req['members']:
            hosts.append(vip['name'])
    except:
        print "Couldn't find \"name\" in Libra response."
        return False

    for vip in sorted(set(hosts)):
        CURL_HOSTS.append(CurlHost(vip,False))

    # Everything worked!!!
    return True

def getYesOrNo(strToDisplay):
    '''
    This displays the inputted string and returns "y" or "n"

    @params
        strToDisplay - Y/N question to prompt the user for

    @returns
        "y" - if the user inputs "y"
        "n" - if the user inputs "n"
    '''

    getch = _Getch()

    while True:
        print strToDisplay,
        x = getch()
        if 'y' in x:
            print x
            return "y"
        elif 'n' in x:
            print x
            return "n"
        elif '^C' in x:
            exit()
        else:
            print x
            pass

def hitTheVip():
    '''
    This iterates only on the vip, and not the hosts in the vip.
    The host that returns is determined by the vip, not by this program.
    '''

    threads = []

    # Prompt user for iterations
    setNumIterations()

    # Prompt user for new response time threshold
    setResponseTime()

    # Prints out all the pre-curl info to the user
    printInfoToUser()

    # Add CurlHost about
    CURL_HOSTS.append(CurlHost(VIP,True))

    CURL_HOSTS[0].run()

    #for result in CURL_HOSTS[0].results:
    #    print "Resultcccccccc:"
    #    for i in result:

    #        print i

    # Wait for all threads to finish
    #for t in threads:
    #    t.join()


    # Print results out to user
    print_curl_results()

    print_vip_results()
    print_viptime_errors()
    print_error_hosts()

def parseClArgs(argv):
    '''
    Splits up the inputted arguments from the command line and assigns them
    to the correct variables

    @Params
        argv - list of command line arguments
    '''

    global ITERATIONS
    global VIP
    global PAGENAME
    #global SAVE_FILENAME

    parser = argparse.ArgumentParser()

    parser.add_argument('--vipname',
                        '-vip',
                        help="Name of vip to curl against",
                        nargs=1,
                        action='store',
                        required=True)
    parser.add_argument('--iterations',
                        '-n',
                        help="Number of times to curl against each host in the vip",
                        action='store',
                        required=True)
    parser.add_argument('--url',
                        '-u',
                        help="Full url that you want tested",
                        nargs=1,
                        action='store',
                        required=True)
    parser.add_argument('--write-to',
                        '-w',
                        help="Name of file to write results to",
                        nargs=1,
                        action='store')


    args = parser.parse_args()

    # Assign variables found through parser
    iterations = int(args.iterations)
    vip = args.vipname[0]
    parse_url(args.url[0])
    #SAVE_FILENAME = str(args.write_to[0])

def parse_url(fullUrl,isVip):
    '''
    This parses the url and figures out what is the pagename and element if
    it's a full pagename. If it's a vip then it just gets the raw vip name.

    @params
        fullUrl - full string that should be stripped/parsed
        isVip - Boolean to tell whether this is a vip or not
    '''


    global PAGENAME
    global ELEMENT
    global VIP

    fullUrl = (fullUrl.lstrip()).rstrip()
    p = fullUrl
    urlParts = []

    # Parse the input string
    if fullUrl.startswith("www."):

        if '.com/' in fullUrl:
            urlParts = (fullUrl.split('www.')[1]).split('.com/')
        else:
            urlParts = (fullUrl.split('www.')[1]).split('.com')

        p = urlParts[0] + ".com"

    elif fullUrl.startswith("https://"):

        if '.com/' in fullUrl:
            urlParts = (fullUrl.split('https://')[1]).split('.com/')
        else:
            urlParts = (fullUrl.split('https://')[1]).split('.com')

        p = urlParts[0] + ".com"

    elif fullUrl.startswith("http://"):

        if '.com/' in fullUrl:
            urlParts = (fullUrl.split('http://')[1]).split('.com/')
        else:
            urlParts = (fullUrl.split('http://')[1]).split('.com')

        p = urlParts[0] + ".com"

    elif ".com/" in fullUrl:

        urlParts = fullUrl.split('.com/')
        p = urlParts[0] + ".com"

    elif ".com" in fullUrl:

        urlParts = fullUrl.split('.com')
        p = urlParts[0] + ".com"

    elif ".net/" in fullUrl:

        urlParts = fullUrl.split('.net/')
        p = urlParts[0] + ".net"

    elif ".net" in fullUrl:

        urlParts = fullUrl.split('.net')
        p = urlParts[0] + ".net"

    # If there's an element then assign it
    if len(urlParts) > 1:
        e = ''.join(urlParts[1:])


    # Assign the variables to the global variables
    if isVip is False:
        PAGENAME = p
        ELEMENT = e
    else:
        VIP = p

def print_curl_results():
    '''
    Outputs all the retrieved curl results to the user
    '''

    global CURL_HOSTS

    # Loop through each CurlHost object and print the results
    for curlhost in CURL_HOSTS:

        # Print Hostname
        print "\n"+curlhost.hostname

        # Print all the data
        #
        # singleCurlCommand Format:
        #       [0] - Curl Command Output
        #       [1] - number assigned for splunk
        #       [2] - string assigned for splunk

        for singleCurlCommand in curlhost.results:
            print singleCurlCommand[0]


    print "######################################"
    print "Errors found with these:"
    print "######################################\n"


    # Check to see if there are any 4xxs or 5xxs and print if there are
    for i in CURL_HOSTS:
        if i.fiveHunds != "" or i.fourHunds != "":
            print i.hostname +"\n"+i.fourHunds+"\n"+i.fiveHunds

def print_error_hosts():
    '''
    This is used to print all error hosts in the vip command.
    This is only used with option 3.
    '''

    # Check if there are any hosts in here
    if len(CURL_HOSTS[0].problemHosts) is 0:
        return

    print "--------------------------------------------"
    print "#          Host Error Count                #"
    print "--------------------------------------------"
    print " "




    print "               HOST                         NUM ERRORS    "
    print "-"*53

    for k in sorted(CURL_HOSTS[0].problemHosts, key=CURL_HOSTS[0].problemHosts.get, reverse=True):
        hostcharsLeft = 37 - len(k)
        countCharsLeft = 2 - len(str(CURL_HOSTS[0].problemHosts[k]))
        #print k + " - " + str(CURL_HOSTS[0].problemHosts[k])
        print "|  "+k,
        print " "*hostcharsLeft,
        print "|    ",
        print str(CURL_HOSTS[0].problemHosts[k]),
        print " "*countCharsLeft,
        print "|"
        print "|"+"-"*51+"|"


def printInfoToUser():
    '''
    Prints out all the curl information to the user
    '''

    # Print out the information that the user inputted (for double checking)
    print "\nPage Name: " +Colors.OKBLUE+PAGENAME+Colors.ENDC

    # Check if there's an element or not
    if ELEMENT == "":
        print "Element: "+Colors.ERROR+"None"+Colors.ENDC
    else:
        print "Element: "+Colors.OKBLUE+ELEMENT+Colors.ENDC

    print "Vip: "+Colors.OKBLUE+VIP+Colors.ENDC+"\n"

def printOverThresholdReturns():
    '''
    This calculates any returns that are over the RESPONSE_TIME_THRESHOLD
    and prints them out to the user with a splunk link (Splink)
    '''

    # Calculate overThresholdReturns
    overThresholdReturns = findOverThresholdReturns()

    # See if any overThresholdReturns are found
    if len(overThresholdReturns) > 0:

        print "\nWe found some returns over threshold: \n"

        # Output the overThresholdReturns
        for i in overThresholdReturns:
            print "---------------------------------------------------------"
            print i[0]+":"
            print "    "+i[1]
            print "    Special Key: "+i[3]
            print "    Identifier: "+str(i[2])
            # link removed for security reasons
            print "---------------------------------------------------------"

def print_vip_results():
    '''
    This prints results of the vip errors found running the sole vip command
    This is only used when option 3 is ran
    '''

    # Make sure there are errors first
    if len(CURL_HOSTS[0].vipReturns_Errors) is 0:
        return

    print "--------------------------------------------"
    print "#          RETURN CODE ERRORS              #"
    print "--------------------------------------------"

    for error in CURL_HOSTS[0].vipReturns_Errors:
        print "Found error: "+Colors.ERROR+str(error[0])+Colors.ENDC
        print "   "+error[1]+"\n"

    print " "

def print_viptime_errors():
    '''
    This prints the errors in response time in a vip check.
    This is only used when option 3 is ran
    '''

    # Make sure there are errors first
    if len(CURL_HOSTS[0].vipReturnTime_Errors) is 0:
        return

    print "--------------------------------------------"
    print "#          RETURN TIME ERRORS              #"
    print "--------------------------------------------"

    for error in CURL_HOSTS[0].vipReturnTime_Errors:
        print "Response Time Error: "+Colors.ERROR+str(error[0])+Colors.ENDC
        print "   "+error[1]+"\n"

    print " "

def randomword(length):
    '''
    Gets a random word/string that is used for each CurlHost object
    '''
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

def reset_variables():
    '''
    This is called every time before running another iteration of the program.

    This is to ensure that nothing is forgotten to be reset.
    '''

    global RESPONSE_TIME_THRESHOLD, TOTALTHREADS, NUMEXITED

    # Reset results of hosts in curl command
    for curlhost in CURL_HOSTS:
        curlhost.reset_results()

    # Reset threshold
    RESPONSE_TIME_THRESHOLD = 10

    # Reset thread count
    TOTALTHREADS = 0

    # Reset number of threads exited
    NUMEXITED = 0

def run_basic_curl():
    '''
    This is called when the user chooses to just run the basic curl check which
    is NOT iterative. It just simply runs one curl check that returns all the redirects
    until a non-redirect is given.
    '''

    global PAGENAME

    print "Running...\n"

    # Run curl request
    basic_curl = subprocess.Popen(["curl -o /dev/null -sD - -kLH \"Host: "+PAGENAME+"\" https://"+VIP+"/"+ELEMENT+"  ; printf \"Curl Exit Code: $?\""], stdout=subprocess.PIPE, shell=True)
    (out, err) = basic_curl.communicate()

    # Check if the error code is NOT 0
    if out.split("Curl Exit Code: ")[1] is not "0":
        print "\n\nExit Code Page: "+Colors.OKBLUE+"https://curl.haxx.se/libcurl/c/libcurl-errors.html\n"+Colors.ENDC

    # Output the curl results
    print "****************************"
    print Colors.OKBLUE +out+Colors.ENDC
    print "****************************"

def run_curl_threads():
    '''
    This runs all the curl commands for all the CurlHosts
    '''

    # Variable to keep track of all threads
    threads = []

    print "Gathering your requested results. This may take a moment..."
    # Start all the curl threads
    for curlhost in CURL_HOSTS:
        tmp_thread = Thread(target = curlhost.run)
        tmp_thread.start()
        threads.append(tmp_thread)

    # Wait for all threads to finish
    for t in threads:
        t.join()

def save_to_file_option():
    '''
    Asks the user if they'd like to save to file
        - If yes, it writes to the file
    '''

    global CURL_HOSTS

    # Ask if they want to save to file
    rtf = getYesOrNo("Write test restults to file? ("+Colors.OKGREEN+"y"+Colors.ENDC+"/"+Colors.ERROR+"n"+Colors.ENDC+"):")

    # Write to file if they input "y"
    if rtf is "y":

        # Get the filename from the user
        filename = raw_input("Please enter filename to save to: ")

        # Make sure that they inputted the correct filename
        while True:
            yorn = getYesOrNo(filename+"? ("+Colors.OKGREEN+"y"+Colors.ENDC+"/"+Colors.ERROR+"n"+Colors.ENDC+")")
            if yorn is "y":
                break
            elif yorn is "n":
                filename = raw_input("Please enter filename to save to: ")
                continue
            else:
                pass

        # Write to filename
        file = open(filename,"w")
        with open(filename,"w") as f:
            for curlhost in CURL_HOSTS:
                f.write("\n"+curlhost.hostname+"\n")
                for result in curlhost.results:
                    f.write(result[0]+"\n")

def setNumIterations():
    '''
    This prompts the user for the number of iterations they desire.
    It then stores i in the global variable ITERATIONS
    '''

    global ITERATIONS

    # Communicate what number of iterations is
    print "\n"+Colors.OKBLUE+"Number of Iterations - number of times to curl against "+Colors.ERROR+"each host"+Colors.OKBLUE+" in the vip"+Colors.ENDC+"\n"

    # Get number of iterations
    while True:
        # Error check to make sure they input an integer
        try:
            iter_input = int(raw_input("Number of Iterations: "))
            break
        except:
            print "Please make sure to input an integer."
            continue

    # Set ITERATIONS
    ITERATIONS = iter_input

def setResponseTime():
    '''
    Prompts the user for a new response time threshold and sets the
    global variable RESPONSE_TIME_THRESHOLD
    '''

    global RESPONSE_TIME_THRESHOLD

    # Prompt for new response time to look for
    if getYesOrNo("Default Response time threshold is 10s. Set new threshold (y/n)?:") is "y":
        while True:
            # Get new threshold from the user
            try:
                RESPONSE_TIME_THRESHOLD = int(raw_input("New response time threshold in seconds: "))
                break
            except:
                print "Please make sure to input an integer."
                continue

def updatePercent():
    '''
    This is used to output the progress of the threads to the user.
    '''

    global TOTALTHREADS
    global NUMEXITED

    if TOTALTHREADS == 0:
        TOTALTHREADS = ITERATIONS * len(CURL_HOSTS)


    # This is used if you want a count:
    #        Number of threads exited / Total Number Running

    EXIT_COUNT_LOCK.acquire()

    NUMEXITED += 1

    # IF all threads have exited
    if NUMEXITED == TOTALTHREADS:
        print "\r",
        print Colors.OKGREEN+str(NUMEXITED)+"/"+str(TOTALTHREADS)+" complete!"+Colors.ENDC
        NUMEXITED = 0
        TOTALTHREADS = 0
        print "Done."
        EXIT_COUNT_LOCK.release()
        return

    # This is used if you want a percentage

    #numExited = float(numExited) + 1
    #newPercent = int((numExited/len(curl_hosts))*100)
    #newPercent = int((numExited/totalThreads)*100)
    #if newPercent == 100:
    #    print "\r",
    #    print Colors.OKGREEN+"100% Complete"+Colors.ENDC
    #    numExited = 0
    #    totalThreads = 0
    #    print "Done."
    #    exitCountLock.release()
    #    return

    print "\r",
    print str(NUMEXITED)+"/"+str(TOTALTHREADS)+" complete",
    sys.stdout.flush()

    EXIT_COUNT_LOCK.release()

def main(argv = sys.argv):

    global HELPER_MODE

    # Check if ran with arguments or not
    if len(argv) > 1:
        HELPER_MODE = False

    # Print main program greeting
    print Colors.PURPLE+"""

########################################################
#|                                                    |#
#| """+Colors.BLUE+"""Welcome to the Rockin Sockin Curl Command Program! """+Colors.PURPLE+"""|#
#|              """+Colors.BLUE+"""We're glad you're here."""+Colors.PURPLE+"""               |#
#|                                                    |#
########################################################

    """+Colors.ENDC

    # Choose whether or not to run interactively
    if HELPER_MODE is True:
        get_curl_info()
        display_menu_get_input()

    else:
        parseClArgs(argv)
        curl_return_codes_MAIN()
        exit()

if __name__ == "__main__":

    #main()
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        print " "
        exit()
