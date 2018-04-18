import argparse
import mts
import sys


def main():
    parser = argparse.ArgumentParser('specify a name or pattern to change mintty theme')
    parser.add_argument('pattern', nargs='?', help='pattern to match against theme filenames (list available themes when omitted)')
    args = parser.parse_args()
    if args.pattern:
        try:
            mts.select_theme(args.pattern)
        except mts.NoMatchingThemeFoundException:
            sys.stderr.write('No matching theme found\n')
            exit(1)
    else:
        themes = mts.find_themes()
        if len(themes) == 0:
            print('No themes found\n')
        else:
            for theme in themes:
                print(theme)


if __name__ == '__main__':
    main()
