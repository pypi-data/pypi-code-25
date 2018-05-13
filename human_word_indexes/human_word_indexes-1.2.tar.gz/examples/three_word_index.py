import logging

from human_word_indexes.word_index_generator import WordIndexFilter
from human_word_indexes.word_index_generator import WordIndexGenerator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':
    twi = WordIndexGenerator(10)
    logger.info(twi.generate_word_index())
    word_filter = WordIndexFilter().set_max_length(5).set_min_length(1)
    twi = WordIndexGenerator(5, word_count=2, word_filter=word_filter)
    logger.info(twi.generate_word_index())
    logger.info('Using custom vocabulary')
    twi = WordIndexGenerator(10,custom_corpus=open('food_words.txt','r').read().split('\n'))
    logger.info(twi.generate_word_index())
