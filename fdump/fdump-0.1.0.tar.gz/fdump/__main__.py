"""
Main module for fdump command line utility.
"""
import re
import sys
import os
import signal

def signal_handler(signal, frame):
    os.system('setterm -cursor on')
    sys.exit(0)

def usage():
    app_name = os.path.basename(__file__)
    print("""
    Tool for spliting stream lines based on regular expression matching. Each line from STDIN
    will be sent to dump file if it matches given regular expression and a dump file path is
    specified or to STDOUT if it doesn't match. Lines will always be appended to the end of a
    dump file. Multiple `-d` and `-g` options can be used, each receiving and processing  the
    output of previous one.

    Usage:
       {0} [OPTIONS]

    Options:
        -d REGEX [DUMPFILE] -   Lines from STDIN or previous -d/-g that match REGEX will be
                                dumped to DUMPFILE file or /dev/null if used without DUMPFILE.
                                The rest goes to the next -d/-g or if this is the last one, to
                                STDOUT.

        -g REGEX [DUMPFILE] -   Same as -d but inverted: matching regexes are printed or passed
                                and non matching are dumped to DUMPFILE or /dev/null.

        -p REGEX [OUTPUT]   -   Lines from STDIN or previous -d/-g will be parsed using regex 
                                and the output will be comma separated regex groups, or if
                                OUTPUT is defined, it will substitute '{{N}}' strings in OUTPUT
                                with group number N. It will then pass this to next -d/-g or -p
                                filter or print it to the output.

        -h                  -   Show this help and exit.
    
    Example:
        {0} -g query -d user ~/user_queries.txt -d script ~/script_queries.txt > rest.txt
    """.format(app_name))

def err_unrecognized_option(opt):
    print("ERROR: Unrecognized option: '{}'.".format(opt))
    usage()
    sys.exit(1)

def err_invalid_numargs(opt, args=None):
    print("ERROR: Used option '{}' with invalid number of arguments:".format(opt))
    print(str(opt) + " " + " ".join(args))
    usage()
    sys.exit(1)


def get_filters():
    filter_lists = []
    args = sys.argv[1:]
    while len(args):
        if args[0][0] is '-':
            action = None
            opt = args.pop(0)
            if opt == '-d':
                action = 'dump' 
            elif opt == '-g':
                action = 'grep'
            elif opt == '-p':
                action = 'parse'
            elif opt in ('-h', '--help'):
                usage()
                sys.exit(0)
            else:
                err_unrecognized_option(opt)
            fltr = []
            fltr.append(action)
            while len(args) and args[0][0] != "-":
                fltr.append(args.pop(0))
            if len(fltr) < 2 or len(fltr) > 3: err_invalid_numargs(opt, fltr[1:])
            filter_lists.append(fltr)
    filters = []
    for values in filter_lists:
        # Opening a file for each filter.
        fltr = {}
        fltr['action'] = values[0]
        fltr['regex'] = values[1]
        if len(values) == 3:
            if fltr['action'] == 'parse':
                fltr['print'] = values[2]
            else:
                fltr['dumpfile'] = values[2]
        filters.append(fltr)
    return filters


def fdump(stdin, stdout, filters):
    # convert file names to files
    for fltr in filters:
        if 'dumpfile' in fltr and fltr['dumpfile']:
            fltr['dumpfile'] = open(fltr['dumpfile'], 'a')
        else:
            fltr['dumpfile'] = None
    for line in stdin:
        for fltr in filters:
            if fltr['action'] == 'parse':
                res = re.search(fltr['regex'], line)
                if res:
                    if 'print' in fltr:
                        try:
                            new_line = fltr['print'].format(*res.groups())
                            line = new_line + '\n'
                        except:
                            line = None
                    else:
                        new_line = ", ".join(res.groups())
                        line = new_line + '\n'
                else:
                    line = None
            else:
                matched_a_filter = bool(re.search(fltr['regex'], line))
                if fltr['action'] == 'grep': matched_a_filter = not matched_a_filter
                if matched_a_filter:
                    if fltr['dumpfile']:
                       fltr['dumpfile'].write(line)
                    line = None
                    break
        if line:
            stdout.write(line)
    for fltr in filters:
        # Close all opened files.
        if fltr['dumpfile']:
            fltr['dumpfile'].close()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    filters = get_filters()

    if not len(filters):
        # No filters defined so I will act as a pipe.
        for line in sys.stdin:
            sys.stdout.write(line)
        sys.exit(0)

    fdump(sys.stdin, sys.stdout, filters)
    sys.exit(0)

if __name__ == '__main__':
    main()


