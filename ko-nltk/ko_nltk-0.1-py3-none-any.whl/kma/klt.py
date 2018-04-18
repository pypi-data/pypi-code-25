# -*- coding:utf8 -*-
# Korean Natural Language Toolkit : Klt 한국어 형태소 분석기
#
# Copyright (C) 2017 - 0000 KoNLTK project 
# Author: Younghun Cho <cyh905@gmail.com>
#         HyunYoung Lee <hyun02.engineer@gmail.com>
#         GyuHyeon Nam <ngh3053@gmail.com>
#         Seungshik Kang <sskang@kookmin.ac.kr>
# URL: <http://www.konltk.org>
# For license information, see LICENSE.TXT

"""
Klt 한국어 형태소 분석기

klt 한국어 형태소 분석기는 국민대학교 강승식 교수님이 만든 형태소 분석기 입니다.
더 많은 정보를 보실려면 http://nlp.kookmin.ac.kr/HAM/kor/index.html 에서 보시면 됩니다.

현재 klt는 analyze, morphs, nouns 기능을 제공합니다.
모든 기능을 사용하기 위해서는 dictionary를 초기화해야합니다.
dictionary는 konltk설치시 "/konltk"에 설치가 됩니다.
만약 다른 위치에 있으면 dic_init함수를 써서 초기화하면 됩니다.

그리고 각 기능을 사용할때 libindex.so.3 라이브러리 파일이 필요합니다.
libindex.so.3 파일이 환경변수에 "LD_LIBRARY_PATH"에 있어야 합니다.
정상적으로 설치되어 있었다면 라이브러리 파일은 /konltk에 있습니다.
설치 후 바로 사용하실려면
    $ source /etc/profile
명령어를 사용하면 사용 가능하고, 설치 후 재부팅을 하시면 따로 명령어 없이 사용 가능합니다.

사용하기전에
    $ export LD_LIBRARY_PATH="/konltk"
를 실행하면 더욱 안전하게 사용 가능합니다.

Example:
    >>> from konltk.kma.klt import Klt
    >>> k = Klt()
    >>> simple_txt = "안녕하세요. 좋은 아침입니다."
    >>> k.analyze(simple_txt)
    [('안녕하세요', [('안녕', 'N'), ('하', 't'), ('세요', 'e')]), ('.', [('.', 'q')]), ('좋은', [('좋', 'V'), ('은', 'e')]), ('아침입니다', [('아침', 'N'), ('이', 'c'), ('습니다', 'e')]), ('.', [('.', 'q')])]
    >>> k.morphs(simple_txt)
    ['안녕', '하', '세요', '.', '좋', '은', '아침', '이', '습니다', '.']
    >>> k.nouns(simple_txt)
    ['안녕', '아침']
"""
from konltk.kma.api import KmaI

from konltk.kma.lib.klt.python3 import kma
from konltk.kma.lib.klt.python3 import index

class Klt(KmaI):
    """
    국민대학교 강승식 교수님의 KLT2000입니다
    """

    def __init__(self, dic_path="/konltk/kma/klt"):
        """
        Args:
            dic_path(str): 사전 위치
        """

        self.dic_init(dic_path)

    @staticmethod
    def dic_init(dic_path="/konltk/kma/klt"):
        """사전을 초기화하는 함수입니다.
        Args:
            dic_path(str): 사전 위치
        """
        kma.init(dic_path) # pylint: disable=I1101
        index.init(dic_path) # pylint: disable=I1101
        return

    def analyze(self, _input):
        """문장을 입력받아 모든 형태소/품사 후보군들을 출력합니다.

        Args:
            _input(str): 형태소/품사 분석한 문장

        Returns:
            (원본, [(형태소, 품사)]) list
        """
        return kma.morpha(_input)[1] # pylint: disable=I1101

    def morphs(self, _input):
        """문장을 입력받아 형태소만 출력합니다.

        Args:
            _input(str): 형태소를 분석한 문장

        Returns:
            형태소 분석된 list
        """
        morpha = kma.morpha(_input)[1] # pylint: disable=I1101

        list_morphs = []

        for i in morpha:
            for j in i[1]:
                list_morphs.append(j[0])

        return list_morphs

    def nouns(self, _input):
        """문장을 입력받아 색인어들을 출력합니다.

        Args:
            _input(str): 색인어 추출한 문장

        Returns:
            색인어가 추출된 list
        """
        _index = index.index(_input) # pylint: disable=I1101

        list_nouns = []

        for i in _index:
            if i[1]:
                list_nouns.append(i[1][0])

        return list_nouns
