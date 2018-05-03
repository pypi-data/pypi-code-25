import pickle
import sys
import os

from MKGen.utils import load_message, Parser
from MKGen.corpus import create_corpus

from MKGen import settings


def train():
    try:
        path_name = sys.argv[1]
    except IndexError:
        path_name = 'asuka'
    input_file = path_name + '.txt'
    output_file = path_name + '.pkl'
    input_path = os.path.join(settings.DATA_DIR, input_file)
    output_path = os.path.join(settings.MODEL_DIR, output_file)

    parser = Parser()
    lines = load_message(input_path)
    model = {}

    for line in lines:
        line = parser.clean(line)
        words = parser.parse(line)
        model.update(create_corpus(words, model))
    with open(output_path, 'wb') as f:
        pickle.dump(model, f)


if __name__ == '__main__':
    train()
