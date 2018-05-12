# -*- coding: utf-8 -*-
"""OpenMaker text utilities.

The module holds a set of utilities for data handling and io related tasks.

Author: Bulent Ozel
e-mail: bulent.ozel@gmail.com

"""

import pprint as pp
import pandas as pd


def format_output_fname(current_theme):
    """Formatting output file name.
    
    """
    output_fname = "_".join([word.capitalize() for word in current_theme.split(" ")])
    return output_fname


def load_from_file(fname):
    """The method reloads a new stopwords list.

    Note:
        Internal stopword is overwritten.

    Args:
        fname (:obj:`str`): a file path string

    Returns:
        (:obj:`set`): The list of terms

    """
    try:
        with open(fname, "r") as f:
            return list(f.read().strip().split("\n"))
    except EnvironmentError:
        print('File access error at {}, data loading is skipped.'.format(fname))
        return []

def pandas_filter_rows(df, col = 'Score', min_t= None, max_t = None):
    """The method extracts rows from a Pandas data frame for the given score range.
    The scores above the minimum and below the maximum is selected.

    Note:
        This function should be generalized so that it can work on any predicate function.

    Args:
        df (:obj:`pandas.core.frame.DataFrame`): A Pandas data frame.
        col (:obj:`str`): The column that the filtering operation to be applied (default 'Score') 
        min_t (:obj:`float`): The minumum score threshold to be included when assigned (default None).
        max_t (:obj:`float`): The maximum score threshold to be included when assigned (default None).

    Returns:
        df (:obj:`pandas.core.frame.DataFrame`): A Pandas data frame.
    
    Raises:
        TypeError: Raised if the column data type is not a number.

    """
    col_type = str(df.dtypes[col])
    if not ('float' in col_type or 'int' in col_type):
        raise TypeError('Column type should be either int or float')
        
    if min_t:
        df = df.loc[df[col] >= min_t]
    
    if max_t:
        df = df.loc[df[col] <= max_t]
    return df


def pandas_rename_cols(df, cols = ['TF', 'wTF', 'Score'], prefix = 'u'):
    """The method renames designated columns of the the pandas data frame.

    Args:
        df (:obj:`pandas.core.frame.DataFrame`): A Pandas data frame.
        cols (:obj:`list` of :obj:`str`): The list of columns to renamed. 
       
    Returns:
        df (:obj:`pandas.core.frame.DataFrame`): A Pandas data frame.

    """
    if len(prefix) > 3:
        prefix = prefix[0:3].capitalize()
    names = {c:str(prefix) +'-'+str(c) for c in cols} if type(cols)==list else cols
    return df.rename(columns=names)


def pandas_merge_dfs(dfs):
    """The method renames designated columns of the the pandas data frame.

    Args:
        df (:obj:`pandas.core.frame.DataFrame`): A Pandas data frame.
        cols (:obj:`list` of :obj:`str`): The list of columns to renamed. 
       
    Returns:
        df (:obj:`pandas.core.frame.DataFrame`): A Pandas data frame.

    """
    if not dfs: return
    cols = set(['Term','Stem','SType', 'wTFref'])
    for df in dfs:
        cols = cols.intersection(df.columns)
    if not cols: return
    DF = dfs[0]
    for d in dfs[1:]:
        DF = pd.merge(DF, d, on=list(cols), how='outer', sort=True)
    rcols = sorted(set(DF.columns).difference(cols))
    order = ['Term', 'Stem'] if  'Stem' in cols else ['Term']
    if  'wTFref' in cols: order = order + ['wTFref']
    if  'SType' in cols: order = order + ['SType']
    order.extend(rcols)
    DF = DF[order]
    return DF
       
        
def run_cleaning_process(Cleaner, tokens,
                         exceptions = [],
                         minL = 1,
                         minF = 4,
                         notallowed = ['*'],
                         logging = True
                        ):
    """Term function cleans and counts the words in the ist.

        Args:
            Cleaner (:obj:`omterms.cleaner.TextCleaner'): The text cleaning object.

            tokens (:obj:`list` of :obj:`str` ): The list of words.

            minL (:obj:`int`): The minimum allowed term length (default 1).

            minF(:obj:`int`): The minimum allowed frequency count for the tabuleted outputs
                (default 4).

            notallowed (:obj:`list` of :obj:`str`, optional): The list of symbols that would flag
                the removal of the term if needed (defualt ['*'])

            exceptions (:obj:`list` of :obj:`str`, optional): The list of exceptions.

            logging (:obj:`bool`): Logging (default True)

        Returns:
            (:obj:`nltk.FreqDist`): Returns the trimmed corpus as the NLTK obj, where essentially
                it is python dictionary cleaned terms. The eys are terms and the values are 
                the frequency counts.

    """
    exp = exceptions
    
    ninit = len(tokens)
    print('Cleaning process: Initial size of tokens = {}'.format(ninit))
    
    TFtokens = Cleaner.clean(tokens,logging = logging)
    print('Reduction due to punctuations and stopwords = {}.'.format(len(tokens) - len(TFtokens)))
   
    uTFtokens = Cleaner.remove_numerals(TFtokens, remove_any = False, exceptions = exp)
    print("Reduction due to all numeral terms = {}".format(len(TFtokens) - len(uTFtokens)))
    TFtokens = uTFtokens
        
    uTFtokens = Cleaner.remove_short_terms(TFtokens, threshold = minL, exceptions = exp)
    print("Reduction due to short terms = {}".format(len(TFtokens) - len(uTFtokens)))
    TFtokens = uTFtokens
    
    uTFtokens = Cleaner.remove_rare_terms(TFtokens, below = minF, exceptions = exp)
    print("Reduction due to rare terms = {}".format(len(TFtokens) - len(uTFtokens)))
    TFtokens = uTFtokens
    
    uTFtokens = Cleaner.remove_numerals(TFtokens, remove_any = True, exceptions = exp)
    print("Reduction due to partially numeral terms = {}".format(len(TFtokens) - len(uTFtokens)))
    TFtokens = uTFtokens
    
    uTFtokens = Cleaner.remove_contains(TFtokens, literals = notallowed, exceptions = exp)
    print("Reduction due to terms with not allowed symbols = {}".format(len(TFtokens) - len(uTFtokens)))
    TFtokens = uTFtokens
    
    reduction = ninit - len(TFtokens)
    print("The total term count reduction during this cleaning process = {}".format(reduction))
    if ninit > 0:
        print("Percentage = {}%".format(round(100.0 * reduction/ninit),2))
    return TFtokens


def run_tokenizing_process(text, tokenizer):
    """The functions tokenizes the given input text.

        Args:
            text (:obj:`str` ): The input text.
            
            tokenizer (x :obj:`str` -> y: :obj:`str`): The tokenizer function.

        Returns:
            (:obj:`list` of :obj:`str` ): The list of words as tokens.

    """
    print('Tokenizing the input text ..')
    tokens = tokenizer(text)
    print('Done. Number of terms: {}'.format(len(tokens)))
    return tokens

def run_stemming_process(theCorpus, stemf):
    """The functions computes the stems of terms in the corpus.

        Args:
            theCorpus (:obj:`omterms.datauis.Corpus`): The text corpus.
          
        Returns:
            theCorpus (:obj:`omterms.datauis.Corpus`): The text corpus.

    """
    print('Stemming the terms in the corpus ..')
    theCorpus.set_stemmer(stemf)
    theCorpus.compute_stems()
    print('Done.')
    return theCorpus


def summary_corpus(SC, top = 20, bottom = 20):
    """The functions computes the stems of terms in the corpus.

        Args:
            SC (:obj:`omterms.datauis.Corpus`): The text corpus.
            top (:obj:`int`): The top most common items to be displayed (default 20).
            bottom (:obj:`int`): The least common items to be displayed (default 20).
            
        Returns:
            (:obj:`pandas.DataFrame`) The tabulated data

    """
    print('Number of unique words = {}'.format(SC.get_count_uniques()))
    print('Number of words = {}'.format(SC.get_size()))
    print('\nMost frequents ::>>')
    pp.pprint(SC.get_top_frequents(top = top))
    print('\nLeast frequents ::>>')
    pp.pprint(SC.get_least_frequents(bottom = bottom))
    SC.plot(top), SC.plot(top, cumulative = True)
    SC.tabulate(7)
    return SC.to_pandas()

