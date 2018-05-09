from abc import ABCMeta, abstractmethod
import os
from extractor.configuration import Configuration as Config
from extractor.root import path

class AbsEnhancer:

    def __init__(self, questions):
        self._runtimePath = None
        self._questions = questions

    # this is called autom. by the extractor
    def enhance(self, document):

        id = self.get_enhancer_id()

        for question in self._questions:
            candidates = document.get_answer(question)
            for candidate in candidates:
                # offset aka text position of this candidate
                # character_offset = candidate.get_parts_character_offset()

                process_data = document.get_enhancement(id)
                if process_data is not None:
                    for part in candidate.get_parts():
                        begin = part[0]['nlpToken']['characterOffsetBegin']
                        end = part[0]['nlpToken']['characterOffsetEnd']
                        character_offset = (begin, end)

                        # call enhancer implementation
                        data = self.process_data(process_data, character_offset)

                        if data:
                            part[0][id] = data


    def is_overlapping(self, a, b):
        return max(a[0], b[0]) <= min(a[1], b[1])

    def get_path_to_runtime(self):
        if not self._runtimePath:
            self._runtimePath = path( './../' + Config.get()['Giveme5W-runtime-resources'])
        return self._runtimePath


    @abstractmethod
    def get_enhancer_id(self):
        print('TODO: return a unique string to identify this enhancer')
 
    @abstractmethod
    def process(self, document):
        """
        this i called once per document
        :param document: 
        :return: 
        """
        return None

   
    @abstractmethod
    def process_data(self, process_data, character_offset):
        """
        Called once per relevant token but simplified to character_offset(begin, end)
        simply look up process_data, find matching data via offset and return them if any
        this is information is attached to the token under get_enhancer_id()
        :param process_data: 
        :param character_offset: 
        :return: 
        """
        print('TODO: implement')
