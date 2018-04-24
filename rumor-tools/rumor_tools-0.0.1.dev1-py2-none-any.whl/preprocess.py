#!/usr/bin/env python
# encoding: utf-8


"""
Minimal pre-precessing functions for chinese text.
"""
import os
import re
import urllib
import urllib2
from collections import defaultdict
from functools import partial
from pprint import pprint

import bs4
import jieba
import numpy
from flashtext import KeywordProcessor
from hanziconv import HanziConv
from pyhanlp import HanLP

from zhon.hanzi import punctuation as zh_punctuation
from string import punctuation as en_punctuation

from tools import retry, chinese_sentence_delimiters, timing, print_zh_list, decorator_normal_filter
from pebble import concurrent, ProcessPool

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Running memory for entity query results. 运行时存储.
__query_memory__ = {}
# Total number of "谣言" query results. “谣言”的搜索结果总数.
__rumor_all_count__ = None

decorator_normal_string_filter = partial(decorator_normal_filter,
                                         check=lambda x: len(x) >= 1 and not x.startswith("@"),
                                         logger=logger)


def pmi_query(entity, search_url="http://www.baidu.com/s?{0}"):
    """
    Calculating the point-wise mutual information value for the target entity. 计算潜在目标与'谣言'的PMI值.

    :param search_url: User-defined search url with keyword formatted as {0}. 实体查询网址.

    :param entity: Target entity. 潜在目标.

    :return: None. 无.

    """
    global __query_memory__
    global __rumor_all_count__

    if entity in __query_memory__:
        return __query_memory__[entity]

    pattern = re.compile(ur"([0-9]+)")

    @retry(Exception, tries=5, delay=3, back_off=2, logger=logger)
    def query(intent):
        query_url = urllib.urlencode({"wd": intent})
        page = urllib2.urlopen(search_url.format(query_url), timeout=2).read()
        soup = bs4.BeautifulSoup(page, "lxml")
        num = soup.findAll("div", {"class": "nums"})
        count = int("".join(pattern.findall(list(num[0].children)[-1]))) + 1
        return count

    if __rumor_all_count__ is None:
        __rumor_all_count__ = query("谣言")

    rumor_count = query(entity + " 谣言")
    normal_count = query(entity)

    __query_memory__[entity] = numpy.clip(rumor_count * 1.0 / (normal_count + __rumor_all_count__ - rumor_count),
                                          a_min=0.0,
                                          a_max=1.0)
    return __query_memory__[entity]


@timing
def pmi_multi_query(entities, search_url="http://www.baidu.com/s?{0}"):
    """
    Perform a multi-threaded query for each entity in the string.

    :param entities: A list contains all the entities. 实体列表.

    :param search_url: User-defined search url with keyword formatted as {0}. 实体查询网址.

    :return: A list of query scores.

    """

    query_results_list = []

    def call_back(f):
        query_results_list.append(f.result())

    with ProcessPool(max_workers=8, max_tasks=10) as pool:
        for i in range(0, len(entities)):
            future = pool.schedule(pmi_query, args=[entities[i], search_url])
            future.add_done_callback(call_back)

    return query_results_list


@decorator_normal_string_filter
def cut_words(decoded_raw_text, with_punctuations=False):
    """
    Cut the text into words.

    :param with_punctuations: With punctuations or not.

    :param decoded_raw_text: Raw decoded string

    :return: List of words.
    """
    if with_punctuations:
        return jieba.cut(decoded_raw_text)
    else:
        return jieba.cut(re.sub(ur"[%s]+" % (zh_punctuation+en_punctuation), "", decoded_raw_text))


@decorator_normal_string_filter
def cut_sub_sentences(decoded_raw_text, with_punctuations=False):
    """
    Cut the text into sub sentences.
    :param with_punctuations: With entailing punctuations or not

    :param decoded_raw_text: Raw decoded string

    :return: List of sub-sentences

    """
    if not with_punctuations:
        return re.sub(ur"[%s]+" % (zh_punctuation + en_punctuation), " ", decoded_raw_text).split(" ")
    else:
        return re.split(ur"(.*?[%s]+)" % (zh_punctuation + en_punctuation), decoded_raw_text)


@decorator_normal_string_filter
def cut_sentences(decoded_raw_text, with_punctuations=False):
    """
    Cut the text into sentences while preserving the punctuations within each sentence.

    :param with_punctuations: With entailing punctuations or not

    :param decoded_raw_text: Raw decoded string

    :return: List of sentences(strings)
    """
    if not with_punctuations:
        return re.sub(ur"[%s]+" % chinese_sentence_delimiters, " ", decoded_raw_text).split(" ")
    else:
        return re.sub(ur"[%s]+" % chinese_sentence_delimiters, lambda m: m.group(0) + " ", decoded_raw_text).split(" ")


def extract_entities(decoded_raw_text, types=None):
    """
    Segment the text in to words with fall categories: Person, Location, Organization, All

    :param types: Entity types: ["persons", "locations", "organizations"]

    :param decoded_raw_text: Decoded raw text

    :return: Dictionary of words, with four keys: persons, locations, organizations, all

    """

    tag2type = {"nr": "persons",
                "ns": "locations",
                "nt": "organizations"}

    if types is None:
        types = ["persons", "locations", "organizations"]

    result = {t: set() for t in types}

    for term in HanLP.segment(decoded_raw_text):
        token, tag = term.word, str(term.nature)
        if tag2type.get(tag) in types:
            result[tag2type.get(tag)].add(token)

    return result


@decorator_normal_string_filter
def extract_keywords(decoded_raw_text, num=2):
    return HanLP.extractKeyword(decoded_raw_text, num)


@decorator_normal_string_filter
def extract_phrases(decoded_raw_text, num=2):
    return HanLP.extractPhrase(decoded_raw_text, num)


@decorator_normal_string_filter
def extract_ideas(decoded_raw_text, num=2):
    return HanLP.extractSummary(decoded_raw_text, num)


def simple2tradition(decoded_raw_text):
    """
    Translating simple chinese into a tradition one.

    :param decoded_raw_text: Raw decoded string

    :return: None
    """
    return HanziConv.toTraditional(decoded_raw_text)


def tradition2simple(decoded_raw_text):
    """
    Translating tradition chinese into a simple one.

    :param decoded_raw_text: Raw decoded string

    :return: None
    """
    return HanziConv.toSimplified(decoded_raw_text)


class KeywordDetector(object):
    __instance = None
    __init_flag = False

    def __new__(cls, *args, **kwargs):

        if cls.__instance is None:
            cls.__instance = object.__new__(cls)

        return cls.__instance

    def __init__(self):
        if not KeywordDetector.__init_flag:
            self.processor = KeywordProcessor()
            KeywordDetector.__init_flag = True

    def load_keywords_from_dir(self, dir_path, ditch_prev=False):
        """
        Load keywords from a directory of txt files. Each line is a keyword.

        :param ditch_prev: Whether ditch the existing keywords.

        :param dir_path: Directory of txt files

        :return: None
        """
        if not ditch_prev:
            for root, dirs, files in os.walk(dir_path):
                for f in files:
                    self.processor.add_keywords_from_list(open(os.path.join(root, f)).read().split("\n"))
        else:
            self.processor = KeywordProcessor()
            for root, dirs, files in os.walk(dir_path):
                for f in files:
                    self.processor.add_keywords_from_list(open(os.path.join(root, f)).read().split("\n"))

    def find(self, encoded_raw_text):
        return self.processor.extract_keywords(encoded_raw_text)


if __name__ == "__main__":

    text = """新华社北京4月23日电
        中共中央总书记、国家主席、中央军委主席习近平近日作出重要指示强调，要结合实施农村人居环境整治三年行动计划和乡村振兴战略，进一步推广浙江好的经验做法，建设好生态宜居的美丽乡村。习近平指出，浙江省15
        年间久久为功，扎实推进“千村示范、万村整治”工程，造就了万千美丽乡村，取得了显著成效。我多次讲过，农村环境整治这个事，不管是发达地区还是欠发达地区都要搞，但标准可以有高有低。要结合实施农村人居环境整治三年行动计划和乡村振兴战略，进一步推广浙江好的经验做法，因地制宜、精准施策，不搞“政绩工程”、“形象工程”，一件事情接着一件事情办，一年接着一年干，建设好生态宜居的美丽乡村，让广大农民在乡村振兴中有更多获得感、幸福感。浙江省自2003年实施的“千村示范、万村整治”工程有力支撑浙江乡村面貌、经济活力、农民生活水平走在全国前列，为我国建设美丽中国、实施乡村振兴战略等带来实践经验。截至2017年底，浙江省累计有2.7万个建制村完成村庄整治建设，占全省建制村总数的97%；74%的农户厕所污水、厨房污水、洗涤污水得到有效治理；生活垃圾集中收集、有效处理的建制村全覆盖，41%的建制村实施生活垃圾分类处理。 """
    text = text.decode("utf-8")

    ##############
    #  Cut test  #
    ##############

    # tests = [cut_words, cut_sub_sentences, cut_sentences]
    # for test in tests:
    #     print("*"*100)
    #     results = test(text, with_punctuations=True)
    #     for result in results:
    #         print(result)

    #############
    # QueryTest #
    #############

    # print(pmi_multi_query(("习近平", "周永康", "江泽民", "周恩来")))

    ##############
    # EntityTest #
    ##############

    # from itertools import chain
    # entities = list(chain(*extract_entities(text).values()))
    # print(pmi_multi_query(entities))

    ###############
    # ExtractTest #
    ###############

    # print_zh_list(extract_ideas(text))
    # print_zh_list(extract_keywords(text))
    # print_zh_list(extract_phrases(text))

    ###############
    # KeywordTest #
    ###############

    keyword_detector = KeywordDetector()
    keyword_detector.load_keywords_from_dir("/home/maxen/Documents/Code/PycharmProjects/NLPTools/Data/BannedWords")
    results = keyword_detector.find(text.encode("utf-8"))
    print_zh_list(results)

    pass

