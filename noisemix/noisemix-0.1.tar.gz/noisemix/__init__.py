import fasttext

from noisemix import noise, formats
from noisemix import utils

NOISEMIX_SUFFIX = '.nmx'


def mix(dataset, versions=1, format=None):
    """Generates a noisy version of a dataset"""

    if format:
        format = eval('formats.' + args.format)  # string to cls
        format = format()  # cls to instance

    for line in dataset:

        # print(line)

        if format:
            line, data = format.before(line)

        for i in range(0, versions):
            line = mix_sentence(line);
            if format:
                line = format.after(line, data)
            yield line


def mix_sentence(sentence):
    utils.rand_init()
    words = []
    for word in sentence.split(' '):
        words.append(noise.randnoise(word))
    # noisemix.append_noise(words)
    sentence = (' ').join(words)
    return noise.sentence_noise(sentence)


def _read(path):
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            yield line


def _write(dataset, path):
    with open(path, 'w', encoding='utf-8') as f:
        for line in dataset:
            f.write(line)


def _print(dataset, max_lines=None):
    line_count = 0
    for line in dataset:
        print(line)
        line_count += 1
        if line_count == max_lines:
            return


if __name__ == '__main__':

    import argparse

    parser = argparse.ArgumentParser(description='Generate a noisy version of dataset')
    parser.add_argument('path', metavar='path', type=str,
                        help='the paths to the input data file')
    parser.add_argument('-format', type=str, choices=[None, 'fastText'],
                        help='the format of the input data file', required=True)
    parser.add_argument('-versions', type=int, default=1,
                        help='how many versions to generate per line')
    parser.add_argument('--print', type=int, nargs='?', const=max,
                        help='print the output instead of writing to file, optional value for max lines')
    args = parser.parse_args()

    dataset = _read(args.path)

    mixed_dataset = mix(dataset, versions=args.versions, format=format)

    if args.print:
        _print(mixed_dataset, args.print)
    else:
        _write(mixed_dataset, args.path + NOISEMIX_SUFFIX)
