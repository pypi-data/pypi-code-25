"""Driver to train, evaluate and compare to NLTK."""

# [ Imports ]
# [ -Python ]
import time
import random
import logging
import argparse
from itertools import chain
# [ -Projects ]
from sequence_tagging.process_data import read_data, Type
from sequence_tagging.tagger import Tagger, accuracy, get_loc


def nltk_eval(test_X, test_y):
    import nltk
    tags = []
    for sentence in test_X:
        tags.append(nltk.pos_tag(sentence))
    correct = 0
    total = 0
    sent_correct = 0
    sent_total = 0
    for pred_sent, tags_sent in zip(tags, test_y):
        sentence_correct = True
        for pred, tag in zip(pred_sent, tags_sent):
            if pred[1] == tag:
                correct += 1
            else:
                sentence_correct = False
            total += 1
        if sentence_correct:
            sent_correct += 1
        sent_total += 1
    logging.info(
        " NLTK Tag Accuracy: %d/%d = %.2f",
        correct, total, accuracy(correct, total)
    )
    logging.info(
        " NLTK Sentence Accuracy: %d/%d = %.2f",
        sent_correct, sent_total, accuracy(sent_correct, sent_total)
    )


def make_enum(string):
    if string == "chunk":
        return Type.CHUNK
    elif string == "atis":
        return Type.ATIS
    return Type.POS


def main():
    parser = argparse.ArgumentParser("Sequence Tagger")
    parser.add_argument("type", choices=["train", "eval"])
    parser.add_argument("--iter", "-i", type=int, default=5, dest="iter")
    parser.add_argument(
        "--data", "-d",
        choices=[Type.POS, Type.CHUNK, Type.ATIS], default="pos",
        dest="data", type=make_enum
    )
    parser.add_argument("--compare", "-c", action="store_true")
    args = parser.parse_args()

    if args.data is Type.ATIS:
        test_file = "data/ATIS/test.txt"
    else:
        # POS or Chunk
        test_file = "data/POS/test.txt"
    test_X, test_y = read_data(test_file, args.data)
    model_loc, tag_loc = get_loc(args.data)
    if args.type == "train":
        if args.data is Type.ATIS:
            train_file = "data/ATIS/train.txt"
        else:
            train_file = "data/POS/train.txt"
        train_X, train_y = read_data(train_file, args.data)
        tagger = Tagger()
        tagger.train(train_X, train_y, n_iters=args.iter)
        tagger.save(model_loc, tag_loc)
    tagger = Tagger.load(model_loc, tag_loc)
    t0 = time.time()
    tagger.evaluate(test_X, test_y)
    elapsed_time = time.time() - t0
    logging.info(" Time to run eval: %f", elapsed_time)
    logging.info(" Words per second: %f", len(list(chain(*test_X))) / elapsed_time)
    random_index = random.randint(0, len(test_X))
    print(test_X[random_index])
    print(tagger.tag([test_X[random_index]]))

    if args.data is Type.POS:
        if args.compare:
            t0 = time.time()
            nltk_eval(test_X, test_y)
            elapsed_time = time.time() - t0
            logging.info(" Time to run eval: %f", elapsed_time)
            logging.info(
                " Words per second: %f",
                len(list(chain(*test_X))) / elapsed_time
            )

if __name__ == "__main__":
    main()
