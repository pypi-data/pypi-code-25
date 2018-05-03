import argparse
import sys


from trackclip.player import Player

parser = argparse.ArgumentParser(prog="python3 -m trackclip", description=""
                                             "Annotate videos by adding an automatically moving frame with a label. "
                                             "Hotkeys: "
                                             "ESC\t-- close and save; "
                                             "SPACE\t-- pause/unpause; "
                                             "LEFT ARROW\t-- preview at 2x speed; "
                                             "RIGHT ARROW\t-- preview at x/2 speed; "
                                 )
parser.add_argument('-c', '--codec', type=str, help="Four-letter codec name")
parser.add_argument('-o', '--output', type=str, help="The name of the output file")
parser.add_argument('input', type=str, help="Input filename, can be a video device (ex. /dev/video0)")
args = parser.parse_args()

player = Player(args.input, args.output, args.codec, "Tracker: {}".format(args.input))

while True:
    if player.update() == -1:
        sys.exit()
