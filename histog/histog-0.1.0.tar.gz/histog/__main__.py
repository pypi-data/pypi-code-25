"""
Main module for histog command line utility.
"""
import os
import signal
import sys
import time
import math
import textwrap

def usage():
    print(textwrap.dedent("""
    Description:
        histog - draw histogram based on a set of integers from STDIN. Input is
        a string of integers, one per line. Lines with bad values will simply
        be skipped. Note that graph is rotated by -90 degrees.
    
    Usage: histog [OPTIONS]
    
    Options:
        -h      - display this help and exit
        -c      - graph will display cumulative values
        -r      - reverse order of values
        -p      - show percentage on the right side instead of counts
        -t S    - for long inputs: show results periodically every S seconds
        -s S    - for short inputs: sleep S seconds after every entry
        -l N    - show results for last N values only
        -W      - graph width in number of lines (defaults to available lines)
        -H      - graph height in number of chars (defaults to available chars)

    Example:
        for x in $(seq 1000); do echo $RANDOM; done | histog -p
      """))

def signal_handler(signal, frame):
    os.system('setterm -cursor on')
    sys.exit(0)

class Histogram(object):
    
    def __init__(self):
        self.raw_data = []
        self.hist_data = []
        self.total_calc_time = 0
        self.bad_entries = 0
        self.frame_width = 0
        self.frame_height = 0
        self.hist_data = []
        self.hist_count = 0
        self.hist_min = 0
        self.hist_max = 0
        self.hist_med = 0
        self.hist_sum = 0
        self.hist_avg = 0
        self.frame = ""
        self._info_template = textwrap.dedent("""
        count:       {}
        min:         {}
        max:         {}
        median:      {}
        sum:         {}
        average:     {}
        bad entries: {}
        calc time:   {} ms
        \n"""[1:])

    def add(self, line):
        try:
            self.raw_data.append(int(line.strip()))
        except:
            self.bad_entries += 1

    def calculate_frame(self,
            lines = None,
            columns = None,
            reverse = False,
            sums = False,
            percentage = False,
            last = 0,
            ):
        if len(self.raw_data) < 1:
            return
        start_time = time.time()

        # get terminal width and height
        self.frame_height, self.frame_width = os.get_terminal_size()
        if lines:
            self.frame_width = lines
        if columns:
            self.frame_height = columns
        
        # sort raw data and calculate info values
        sorted_data = self.raw_data[-last:]
        sorted_data.sort()
        self.hist_cnt = len(sorted_data)
        self.hist_min = sorted_data[0]
        self.hist_max = sorted_data[self.hist_cnt-1]
        self.hist_med = sorted_data[int(self.hist_cnt/2)]
        self.hist_sum = sum(sorted_data)
        self.hist_avg = round(self.hist_sum/self.hist_cnt, 2)
        
        # add info values to current frame
        self.frame += self._info_template.format(
            str(self.hist_cnt), 
            str(self.hist_min),
            str(self.hist_max),
            str(self.hist_med),
            str(self.hist_sum),
            str(self.hist_avg),
            str(self.bad_entries),
            round(self.total_calc_time*1000,2),
            )
        
        # calcualte histogram margins
        hist_width_margin = 0
        hist_height_margin = 0
        hist_width_margin += len(self.frame.split('\n'))
        # compensate for last line
        hist_width_margin += 1

        # calculate actual graph width (lines)
        hist_width = self.frame_width - hist_width_margin
        
        # calculate step size (between histogram columns)
        step = int(math.ceil((self.hist_max - self.hist_min + 1) / hist_width))
        if step == 0: step = 1
        # add empty column values to graph list: pairs of (value, count)
        for x in range(self.hist_min, self.hist_max+1, step):
            self.hist_data.append([x, 0])
        
        # populate data to graph
        for value in sorted_data:
            # calculate column where the value falls in
            i = int((value-self.hist_min) / step)
            # increment the column count
            self.hist_data[i][1]+=1
    
        # reversed display
        if reverse:
            self.hist_data = [ x for x in reversed(self.hist_data) ]
    
        # cumulative display
        if sums:
            for i in range(1, len(self.hist_data)):
                self.hist_data[i][1] += self.hist_data[i-1][1]
    
        # used to justify text for X and Y axis values
        hist_graph_max = max([ x for (s,x) in self.hist_data ])
        hist_step_max = max([ s for (s,x) in self.hist_data ])
        rjust_value = len(str(hist_step_max))
    
        # set vertical margin
        hist_height_margin += rjust_value + len("+ ")
        if percentage:
            hist_height_margin += len(" 100.0 %")
        else:
            hist_height_margin += len(" ") + len(str(hist_graph_max))

        # build graph
        for (s, x) in self.hist_data:
            self.frame += "{}{}{}\n".format(
                str(s).rjust(rjust_value)+("- " if reverse else "+ "),
                "█" * int((self.frame_height - hist_height_margin) * x / float(hist_graph_max)) if x>0 else "",
                " " + str(round(100.0*x/self.hist_cnt,2))+" %" if percentage else str(x) if x>0 else ""
                )
        end_time = time.time()
        self.total_calc_time += end_time - start_time

    def clear_and_reset(self):
        diff = self.frame_width - len(self.frame.split('\n')) - 1
        for _ in range(diff):
            self.cprint('')
        print('\x1b[1A' * self.frame_width)
        self.frame = ""
        self.hist_data = []

    def cprint(self, text):
        '''Just like print(), but clears any existing text in the current
        output line before printing.'''
        clear_line='\x1b[2K'
        print(clear_line + text.replace('\n', '\n'+clear_line))

    def draw_frame(self, keep = False):
        if len(self.raw_data) < 1:
            return
        self.cprint(self.frame)
        if not keep:
            self.clear_and_reset()


def main():
    signal.signal(signal.SIGINT, signal_handler)
    histogram = Histogram()
    lines = None
    columns = None
    sums = False
    reverse = False
    percentage = False
    show_periodically = False
    sleep_time = False
    show_last = 0
    if len(sys.argv) > 1:
        args = sys.argv[1:]
        while len(args):
            if args[0] in ("-h", "--help", "help"):
                usage()
                sys.exit(0)
            elif args[0] == "-c":
                sums=True
                args.pop(0)
            elif args[0] == "-r":
                reverse=True
                args.pop(0)
            elif args[0] == "-p":
                percentage=True
                args.pop(0)
            elif args[0] == "-l":
                args.pop(0)
                try:
                    show_last = int(args.pop(0))
                except Exception as e:
                    print("Error: option -l expects an integer")
                    usage()
                    sys.exit(1)
            elif args[0] == "-t":
                args.pop(0)
                try:
                    show_periodically = float(args.pop(0))
                except Exception as e:
                    print("Error: option -t expects an integer")
                    usage()
                    sys.exit(1)
                if show_periodically > 0:
                    os.system('setterm -cursor off')
            elif args[0] == "-s":
                args.pop(0)
                try:
                    sleep_time = float(args.pop(0))
                except Exception as e:
                    print("Error: option -s expects an integer")
                    usage()
                    sys.exit(1)
                if sleep_time > 0:
                    os.system('setterm -cursor off')
                    if not show_periodically:
                        show_periodically = 0.1
            elif args[0] == "-W":
                args.pop(0)
                try:
                    lines = int(args.pop(0))
                except Exception as e:
                    print("Error: option -W expects an integer")
                    usage()
                    sys.exit(1)
            elif args[0] == "-H":
                args.pop(0)
                try:
                    columns = int(args.pop(0))
                except Exception as e:
                    print("Error: option -H expects an integer")
                    usage()
                    sys.exit(1)
            else:
                usage()
                sys.exit(1)

    # load values
    last_time = time.time()
    for line in sys.stdin:
        histogram.add(line)
        if show_periodically:
            time.sleep(sleep_time)
            now_time = time.time()
            if now_time - last_time > show_periodically:
                histogram.calculate_frame(
                    lines,
                    columns,
                    reverse,
                    sums,
                    percentage,
                    show_last,
                    )
                histogram.draw_frame()
                last_time = now_time
    histogram.calculate_frame(
        lines,
        columns,
        reverse,
        sums,
        percentage,
        show_last,
        )
    histogram.draw_frame(True)
    os.system('setterm -cursor on')

if __name__ == "__main__":
    main()


