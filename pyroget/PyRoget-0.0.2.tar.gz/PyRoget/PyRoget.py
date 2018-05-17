import _pickle as cPickle
import os
from collections import defaultdict

_file_path = os.path.dirname(__file__)


class PyRoget(object):

    def __init__(self):
        with open(os.path.join(_file_path, 'roget/thes_dict.txt'), 'rb') as f:
            self.word_categories_dict = cPickle.load(f, encoding='utf-8')
        with open(os.path.join(_file_path, 'roget/thes_cat.txt'), 'rb') as f:
            self.category_word_dict = cPickle.load(f, encoding='utf-8')
        with open(os.path.join(_file_path, 'roget/cat_num.txt'), 'rb') as f:
            self.category_code_dict = cPickle.load(f, encoding='utf-8')
        with open(os.path.join(_file_path, 'roget/node_codes.txt'), 'rb') as f:
            self.node_code_category_dict = cPickle.load(f, encoding='utf-8')
        with open(os.path.join(_file_path, 'roget/code_nodes.txt'), 'rb') as f:
            self.category_node_code_dict = cPickle.load(f, encoding='utf-8')
        with open(os.path.join(_file_path, 'roget/full_childparent.txt'), 'rb') as f:
            self.node_parent_dict = cPickle.load(f, encoding='utf-8')
        # TODO: fix capitalization?
        with open(os.path.join(_file_path, 'roget/num_cat.txt'), 'rb') as f:
            self.code_category_dict = cPickle.load(f, encoding='utf-8')

    def add_custom_words(self, fid='roget/add_words.txt'):
        ''' Load a file of words and connections into THES_DICT '''
        try:
            type(self.added_words) is list
        except:
            self.added_words = []
        with open(fid, 'rb') as f:
            for line in f:
                wd_pair = line.strip().split(',')
                if wd_pair[0] not in self.word_categories_dict:
                    self.word_categories_dict[wd_pair[0]] = [wd_pair[1], ]
                    self.added_words.append(wd_pair[0])
                else:
                    if wd_pair[1] not in self.word_categories_dict[wd_pair[0]]:
                        self.word_categories_dict[wd_pair[0]].append(
                            wd_pair[1])

        self.added_words = list(set(self.added_words))
        print("Words Added to THES_DICT:")
        print(' '.join(self.added_words))

    def extract_words(self, text, lower=True):
        """Removes punctuation from text and returns a list of words

        Arguments:
            text {str} -- text from which to extract words

        Keyword Arguments:
            lower {bool} -- case of words extracted (default: {True})

        Returns:
            list of str -- extracted words
        """

        puncMarks = [',', '.', '?', '!', ':', ';',
                     '\'', '\"', '(', ')', '[', ']', '-']
        for item in puncMarks:
            text = text.replace(item, '')
        if lower:
            lowerText = text.lower()
        textWords = lowerText.split()
        return textWords

    def categorize_word(self, word, levels=0):
        """Gets all base categories of a word, returns list of (cateogry, code)

        Arguments:
            word {str} -- word to categorize

        Keyword Arguments:
            levels {int} -- how many levels above base category (default: {0})

        Returns:
            list of tuple of str or None -- list of (category, code) tuples or
                None, if not found
        """

        if word in self.word_categories_dict:
            cats = [(self.code_category_dict[x], x) for x
                    in self.word_categories_dict[word]]
        else:
            return None
        for _ in range(levels):
            for i, cat in enumerate(cats):
                if cat and cat[1] not in {'A', 'B', 'C', 'D', 'E', 'F'}:
                    node = self.node_parent_dict[cat[1]]
                    cats[i] = (self.node_code_category_dict[node], node)
        return cats

    def categorize_words(self, text, levels=0):
        """Get all categories of a text or list of words

        Arguments:
            text {str | list of str} -- text to categorize

        Keyword Arguments:
            levels {int} -- how many levels up to classify (default: {0})

        Returns:
            list of tuple of str or None -- list of (category, code) tuples or
                None, if not found
        """

        if type(text) == 'str':
            wordlist = self.extract_words(text)
        else:
            wordlist = [x.lower() for x in text if x.isalpha()]
        categorized = [self.categorize_word(x, levels=levels) for x
                       in wordlist]
        return [y for x in categorized for y in x if y] or None

    def get_category_freqs(self, text_list, levels=0):
        '''returns dict of word category frequencies of levels=n for a text,
        throwing out words not in the thesaurus'''
        frequency_counts = defaultdict(lambda: 0)
        bagofwords = self.categorize_words(text_list, levels=levels)
        good_cats = [x for x in bagofwords if x]
        for x in good_cats:
            frequency_counts[x] += 1
        return frequency_counts

    def get_all_category_freqs(self, text_list):
        freqlist = self.get_category_freqs(text_list)
        fulldict = {x: 0 for x in self.code_category_dict.keys()}
        for key in freqlist.keys():
            if key[1] in fulldict:
                fulldict[key[1]] = freqlist[key]
        newdict = {(self.code_category_dict[x], x):
                   fulldict[x] for x in fulldict.keys()}
        return sorted(newdict.items(), key=lambda x: x[0][1])

    def get_category_hierarchies(self, word):
        '''returns full hierarchical paths for word
        from base categories to parent node "WORDS" (code '0');
        also returns distance of each node from word/base category;
        return format tuple: (distance,node)'''
        all_cats = [x for x in self.word_categories_dict[word]]
        syn_paths = []
        for cat in all_cats:
            path = []
            counter = 0
            path.append((counter, self.code_category_dict[cat]))
            node = cat
            while True:
                counter += 1
                parent = self.node_parent_dict[node]
                path.append((counter, self.node_code_category_dict[parent]))
                node = parent
                if parent not in self.node_parent_dict.keys():
                    break
            syn_paths.append(path)
        return syn_paths

    def get_words(self, category):
        '''Returns all words in given base category (accepts code or category name)'''
        if category in self.code_category_dict:
            return (self.code_category_dict[category],
                    self.category_word_dict[category])
        elif category.lower() in self.category_code_dict:
            code = self.category_code_dict[category.lower()]
            return(category.upper(), self.category_word_dict[code])
        return []

    def get_all_related_words(self, word):
        '''given word, return all other words in word's categories'''
        cats = [x for x in self.word_categories_dict[word]]
        return tuple((self.code_category_dict[cat],
                      self.category_word_dict[cat]) for cat in cats)

    def distance_to_node(self, word1, node):
        '''given word and node, return distance (in nodes) from base category to node;
        if node not in path to "WORDS" node, distance equals sum of word's and node's
        path to "WORDS"'''
        if node in self.node_code_category_dict:
            node = self.node_code_category_dict[node]
        wordcats = [x[0] for x in self.categorize_word(word1)]
        word1 = word1.lower()
        distances = []
        paths = self.get_category_hierarchies(word1)
        for path in paths:
            for tup in path:
                if node in tup:
                    distances.append(tup[0])
        if distances == []:
            for cat in wordcats:
                pathlength1 = self.get_category_distance(cat, 'WORDS')
                pathlength2 = self.get_category_distance(node, 'WORDS')
                distances.append(pathlength1 + pathlength2)
        dist = min(distances)
        return dist

    def get_shared_nodes(self, word1, word2):
        '''given two words, returns tuples containing all shared nodes
        and minimum distance between the two words via that node;
        output format tuple: (distance,node)'''
        word1 = word1.lower()
        word2 = word2.lower()
        paths1 = self.get_category_hierarchies(word1)
        paths2 = self.get_category_hierarchies(word2)
        nodes1 = []
        nodes2 = []
        path_lengths = []
        for path in paths1:
            for node in path:
                nodes1.append(node[1])
        for path in paths2:
            for node in path:
                nodes2.append(node[1])
        common_nodes = list(set(nodes1).intersection(set(nodes2)))
        for node in common_nodes:
            distances1 = []
            distances2 = []
            for path in paths1:
                for n in path:
                    if node in n:
                        distances1.append(n[0])
            for path in paths2:
                for n in path:
                    if node in n:
                        distances2.append(n[0])
            path_length = min(distances1) + min(distances2)
            path_lengths.append((path_length, node))
        path_lengths.sort(key=lambda x: x[0])
        return path_lengths

    def get_word_distance(self, word1, word2):
        '''returns minimum distance between two words as int'''
        word1 = word1.lower()
        word2 = word2.lower()
        paths1 = self.get_category_hierarchies(word1)
        paths2 = self.get_category_hierarchies(word2)
        nodes1 = []
        nodes2 = []
        path_lengths = []
        for path in paths1:
            for node in path:
                nodes1.append(node[1])
        for path in paths2:
            for node in path:
                nodes2.append(node[1])
        common_nodes = list(set(nodes1).intersection(set(nodes2)))
        for node in common_nodes:
            distances1 = []
            distances2 = []
            for path in paths1:
                for n in path:
                    if node in n:
                        distances1.append(n[0])
            for path in paths2:
                for n in path:
                    if node in n:
                        distances2.append(n[0])
            path_length = min(distances1) + min(distances2)
            path_lengths.append(path_length)
        distance = min(path_lengths)
        return distance

    def get_category_hierarchy(self, category):
        '''returns path from node to parent node "WORDS"
        and distance from given node to each node in path;
        output format list of tuples: [(distance,node),...]'''
        if category == '0':
            return [(0, 'WORDS')]
        elif category.upper() == 'WORDS':
            return [(0, 'WORDS')]
        elif category.lower() in self.node_code_category_dict.keys():
            cat = category.lower()
        elif category.upper() in self.node_code_category_dict.values():
            cat = self.category_node_code_dict[category.upper()]
        # else:
            # NOTE: MAY NEED RETURN THAT DOESN'T MESS UP DISTANCE CALCULATIONS IN NODE CLUSTRING ALGORITHM BELOW
            # return [(0,'WORDS')]
        path = []
        counter = 0
        path.append((counter, self.node_code_category_dict[cat]))
        node = cat
        while True:
            counter += 1
            parent = self.node_parent_dict[node]
            path.append((counter, self.node_code_category_dict[parent]))
            node = parent
            if parent not in self.node_parent_dict.keys():
                break
        return path

    def get_category_distance(self, category1, category2):
        '''return minimum distance between two categories as int'''
        paths1 = self.get_category_hierarchy(category1)
        paths2 = self.get_category_hierarchy(category2)
        nodes1 = []
        nodes2 = []
        path_lengths = []
        for path in paths1:
            nodes1.append(path[1])
        for path in paths2:
            nodes2.append(path[1])
        common_nodes = list(set(nodes1).intersection(set(nodes2)))
        for node in common_nodes:
            distances1 = []
            distances2 = []
            for n in paths1:
                if node in n:
                    distances1.append(n[0])
            for n in paths2:
                if node in n:
                    distances2.append(n[0])
            path_length = min(distances1) + min(distances2)
            path_lengths.append(path_length)
        distance = min(path_lengths)
        return distance

    def cluster_by_categories(self, wlist, verbose=False, N=0):
        '''returns all nodes that minimize aggregate distance to all words in wordlist;
        output format list of tuples: (node,aggregate distance,average distance per word);
        verbose flag triggers running results; N flag determines number of nearest nodes printed'''
        notwords = []
        wordlist = []
        for word in wlist:
            if word not in self.word_categories_dict.keys():
                notwords.append(self.categorize_word(word))
            else:
                wordlist.append(word)
        word_basecats = []
        if verbose:
            print("excluded words:", notwords)
        node_distances = []
        nodelist = self.node_parent_dict.keys()
        for ndx, node in enumerate(nodelist):
            dists = [self.distance_to_node(word, node) for word in wordlist]
            if verbose:
                print(dists)
            aggdist = sum(dists)
            node_entry = (node, aggdist)
            node_distances.append(node_entry)
            avg_node_distance = aggdist / float(len(wordlist))
            if verbose:
                print(ndx, node, aggdist, avg_node_distance)
        node_distances = sorted(node_distances, key=lambda x: x[1])
        node_distances_named = [(node, self.node_code_category_dict[node], dist, (float(
            dist) / len(wordlist))) for (node, dist) in node_distances]
        distlist = [x[1] for x in node_distances]
        mindist = min(distlist)
        mindist_nodes = [(node, self.node_code_category_dict[node], dist, (float(
            dist) / len(wordlist))) for (node, dist) in node_distances if dist == mindist]
        if N > 0:
            return node_distances_named[:N]
        else:
            return mindist_nodes

    def get_all_categories_batch_by_folder(self, folder, csv=False):
        '''accepts name of folder containing only files'''
        import pandas as pd
        import numpy as np
        from os import listdir
        flist = listdir(folder)[1:]
        headlist = [x[:-4] for x in flist]
        with open(folder + flist[0], 'r') as thefile:
            reader = thefile.read()
            thingy = self.get_all_category_freqs(reader)
            indexlist = [x[0] for x in thingy]
        newarray = []
        for f in flist:
            with open(folder + f, 'r') as current_file:
                text = current_file.read()
            freqs = self.get_all_category_freqs(text)
            newarray.append([x[1] for x in freqs])
        nparray = np.array(newarray, dtype=int)
        nparray = np.transpose(nparray)
        df = pd.DataFrame(nparray, index=indexlist, columns=headlist)
        if csv:
            df.to_csv(folder + 'summary.csv')
        return df
