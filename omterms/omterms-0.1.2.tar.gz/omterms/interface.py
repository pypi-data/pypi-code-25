# -*- coding: utf-8 -*-
"""OpenMaker term extraction application interface.

Author: Bulent Ozel
e-mail: bulent.ozel@gmail.com

The application interface provides an encapsualtion and standardization at preparing a set of texts for
further analyses. The standardized term extraction process covers tokenization, counting both raw and 
normalized, cleaning, stemming(optional), and scoring(optional) chioices. The tabulated output can be
exported in .csv file format and/or Pandas dataframe format.

The input text(s) can be provided in any of the following formats:
- raw text
- tokenized text
- tokenized and counted

In the same manner if a background courpus based scoring is desired then the reference corpus
can be provided in any of the above formats. Depending on the desired actions on the input text,
the output may contain not only raw and normalized term frequency counts but also stems of
the terms its frequency count in the background corpus, when provided, and term's log likelihood
weight wrt to its prevalance in the reference corpus.

For deatils please see the README and tuturials that comes alongs with installation 
of this package.

Attributes:
    OUTPUT_FOLDER (file path): The folder to export the tabulated outputs 
        in .csv files.
    
    OUTPUT_FNAME  (file name): The default output file name where results 
        for multiple texts are merged and presented.
        
    STOPWORDS_STANDARD (file path): The location of standard stopward list,
        if desired and exists.
        
    STOPWORDS_SPECIFIC (file path): The location of topic(s) specific stopward
        list, if desired and exists. 
        
    NOTALLOWED (:obj:`list` of `str`): The list of symbols that would flag the
        removal of the term, if needed.
        
        Note: The removal would not take place if the term is a specific term or
            marked as an exception.
        
    TERMS_SPECIFIC (file path): The location of exception list of terms which is
        shielded from cleaning process, if needed.
        
    TOKENIZER_FUNC (x :obj:`str` -> y: :obj:`str`): A tokenizer function.
    
    STEMMER_FUNC (x :obj:`str` -> y: :obj:`str`): A stemmer function,
        if needed
    
    MIN_LENGTH (:obj:`int`): The minimum allowed term length.
    
    MIN_FREQ (:obj:`float`): The minimum allowed frequency count for
        the tabuleted outputs.
    
    MODEL_THRESHOLD (:obj:`int`): if scoring is requested and if the input text
        is not driven from the reference corpus, then the paramter is used at training
        the predection model for the terms that don't occure in the reference corpus.

Todo:
    * Re-implement the module as a memoized object either via a class or
        a via wrapper function.
    * Add a functionality where the configuration paramters can be loaded
        from a JSON file.
    * Make tokenization an optional process, for the cases where the input
        is already provided in tokens.

"""

import copy

from omterms import tokenizer
from omterms.datauis import WikiArticles, Corpus
from omterms.cleaner import TextCleaner
from omterms.measures import Scoring
from omterms.utilities import *
from omterms.stemmer import porter

OUTPUT_FOLDER = "./output/"
OUTPUT_FNAME = "omterms.csv"

STOPWORDS_STANDARD = "./data/stopwords_standard.txt"
STOPWORDS_SPECIFIC = "./data/stopwords_openmaker.txt"
NOTALLOWED = tokenizer.CHARACTERS_TO_SPLIT
TERMS_SPECIFIC = "./data/specifics_openmaker.txt"

TOKENIZER_FUNC = tokenizer.tokenize_strip_non_words
STEMMER_FUNC = porter

MIN_LENGTH = 1
MIN_FREQ = 1
MODEL_THRESHOLD = 1.0


def extract_terms(texts,
                  tokenizer = TOKENIZER_FUNC,
                  merge = False,
                  min_termlength = MIN_LENGTH,
                  min_tf = MIN_FREQ,
                  topics = [],
                  extra_process = [],
                  stemmer = STEMMER_FUNC,
                  refcorpus = None,
                  export = False,
                  basefname = OUTPUT_FNAME,
                  outputdir = OUTPUT_FOLDER, 
                  notallowed_symbols = NOTALLOWED,
                  nonremovable_terms = TERMS_SPECIFIC,
                  file_standard_stopwords = STOPWORDS_STANDARD,
                  file_specific_sopwords = STOPWORDS_SPECIFIC,
                  regression_threshold = MODEL_THRESHOLD
                  ):
    """
    Term extraction modules main driver function.
 
    Args:
        texts (:obj:`str` or :obj:`dict` of `str` or  :obj:`omterms.WikiArticles`):
        The input text can be any of the following:
                - a string,
                - or a dictionary of strings where the key denotes the topic 
                    or any desired label/annotation regarding the text,
                - or a special data holder which contains labeled text scraped
                    from Wikipedia articles.
                
        tokenizer (x :obj:`str` -> y: :obj:`str`): The tokenizer,
            (defualt omterms.tokenizer.tokenize_strip_non_words).
                
        merge (:obj:`bool`): When a collection of text is provided via a dict or
            WikiArticles, the parmater detertmines whether they should be 
            conactinated for the term extraction (default False).
             
        min_termlength (:obj:`int`): The minimum allowed term length (default 1).
        
        min_tf (:obj:`int`): The minimum allowed frequency count for the tabuleted
            outputs (default 4).
                
        topics (:obj:`list` of `str`, optional): The list of topics from the input
            texts to be considered (default Empty).
            
            If topic list is not provided and the merge is not requested but the
            input text is given either via dict or via the WikiArticles data holder,
            then the topic list will be driven from the input collection automatically.
       
        extra_process (:obj:`list` of `str`, optional): Whether stemming and/or scoring
            is requested (default Empty).
            - 'stem' is used/needed to flag stemming.
            - 'compare' is used/needed to scoring texts against the designated
                reference corpus. 
       
        stemmer (x :obj:`str` -> y: :obj:`str`, optional): A stemmer function,
            if needed (default omterms.stemmer.porter).
       
        refcorpus (:obj:`str`
                   or :obj:`list` of `str`
                   or :obj:`dict` of `str`
                   or :obj:`omterms.WikiArticles`, optional): The reference corpus
                       (Default None)
           The refcorpus can beny of the following:
                - None: if it is none yet the a scoring process is requested then
                    NLTK's Brown corpus is loaded.
                - a string: A plain text.
                - list of words: List of words or tokens.
                - or a dictionary of strings where the text from the text will
                    be unified for the reference corpus.
                - or a special data holder which contains labeled text scraped from
                    Wikipedia articles, where all the texts from the collection will 
                    be combined to be used as the reference background corpus.
    
        export (:obj:`bool`, optional): Whether the resulting tables should be
            exported (default False).
        
        basefname (:obj:`str`, optional): The output table name/prefix. Is effective
            only when export is requested (default 'omsterms.csv').
        
        outputdir (:obj:`str`, optional): The file path, that is the folder to export
            the tabulated outputs in .csv files (default './data/').
        
        notallowed_symbols (:obj:`list` of `str`, optional): The list of symbols 
            that would flag the removal of the term if needed 
            (defualt omterms.tokenizer.CHARACTERS_TO_SPLIT
            
        nonremovable_terms (:obj:`str`, optional): File path to the list 
            of exceptions.
        
        file_standard_stopwords (:obj:`str`, optional): The file path to the 
            standard stopward list, if desired and exists.
            
            Note: The removal would not take place if the term is a specific
                term or marked as an exception.
        
        file_specific_stopwords (:obj:`str`, optional): The file path to a 
            specifix stopward list, if desired and exists.
            
            Note: The removal would not take place if the term is a specific term that
            is if marked as an exception.
        
        regression_threshold (:obj:`float`, optional): if scoring is requested
            and if the input text is not driven from the reference corpus then this 
            paramter is used at training the predection model for the terms that 
            don't occure in the reference corpus (default 1.0).
            
    Returns:
        (:obj:`pandas.DataFrame`, optional) The tabulated data.
        
    """
    
    def get_text(collection = texts, topic = None):
        """"
        Retreives the text from the collection.
        
        """
        if type(collection) is str: return collection
        if topic: 
            if type(collection) is dict:
                return collection[topic]
            elif isinstance(collection, WikiArticles):
                if type(topic) is str: tid = collection.get_theme_id(topic)
                return collection.collate(by_theme_id = tid)
            else:
                return
        else:
            if type(collection) is dict:
                return reduce(lambda x,y: x + " " + y, collection.values(), "")
            elif isinstance(collection, WikiArticles):
                return collection.collate()
            else:
                return
        
    def process(text, export=export, prefix=''):
        """
        Given an input text it extracts, tokenizes, stems(optional)
        and  scores(optional) each extracted text.
            
        """
        print('Extracting the terms ...')
        tokens = run_tokenizing_process(text, tokenizer)
        tf_tokens= run_cleaning_process(Cleaner, tokens,
                                        minL = min_termlength,
                                        minF = min_tf,
                                        notallowed = notallowed_symbols,
                                        logging = False)
        thecorpus = Corpus(tf_tokens)
        if 'stem' in extra_process:
            thecorpus = run_stemming_process(thecorpus, stemmer)      
        if 'compare' in extra_process and ref_corpus:
            myScoring = Scoring(thecorpus,ref_corpus,model_threshold = regression_threshold)
            thecorpus = copy.deepcopy(myScoring.sCorpus)
        print("COMPLETED.")
        df = thecorpus.to_pandas()
        if export: export_as_csv(df,prefix)
        return df
    
    def export_as_csv(df, prefix=''):
        """
        Writes to the csv file.
        
        """
        prefix = str(prefix)
        if prefix:
            csvfile_name = outputdir + prefix + '_' + basefname
        else:
            csvfile_name = outputdir + basefname
            
        with open(csvfile_name, 'w') as csvfile:
            df.to_csv(csvfile_name)
        print('Results are exported to file: {}'.format(csvfile_name))
    
        
    print('Configuring the text cleaner ...')
    Cleaner = TextCleaner()
    Cleaner.load_stopwords(file_standard_stopwords)
    if file_specific_sopwords:
        Cleaner.extend_stopwords(file_specific_sopwords)
    if nonremovable_terms:
        nonremovable_terms = load_from_file(nonremovable_terms)
        Cleaner.set_exceptions(nonremovable_terms)
    
    # Reference corpus if exists:
    if 'compare' in extra_process:
        print('Preparing the reference corpus ::>')
        ref_corpus = None
        ref_tokens = list()
        if refcorpus is None:
            print('Comparions/Scoring is requested but no reference corpus text or tokens is provided.')
            print('Loading nltk.corpus.brown ...')
            from nltk.corpus import brown
            ref_tokens = list(brown.words())
        elif type(refcorpus) is str:
            print('An untokenized reference corpus is identified.')
            print('Tokenizing the reference corpus ...')
            ref_tokens = run_tokenizing_process(refcorpus, tokenizer)
        elif type(refcorpus) is list:
            ref_tokens = refcorpus
        elif type(refcorpus) is dict:
            t = get_text(refcorpus)
            ref_tokens = run_tokenizing_process(t, tokenizer)
        elif isinstance(refcorpus, WikiArticles):
            t = refcorpus.collate()
            ref_tokens = run_tokenizing_process(t, tokenizer)
        else:
            print('A non valid corpus format dedected :{}. Comparisons will be skipped.'.format(type(refcorpus)))
            extraprocs.remove('compare')
            
        # Clean and standardize the reference corpus if identified,    
        if ref_tokens:
            print('Cleaning the reference corpus ...')
            tf_ref_tokens= run_cleaning_process(Cleaner,
                                                ref_tokens,
                                                minL = min_termlength,
                                                minF = min_tf,
                                                logging = False,
                                                notallowed = notallowed_symbols)
            ref_corpus = Corpus(tf_ref_tokens)
            print('Stemming the word in the reference corpus ...')
            ref_corpus = run_stemming_process(ref_corpus, stemmer)
        print('Done: Reference corpus process.')

    
    if type(texts) is str:
        print('A single text is provided.')
        return process(texts)
    
    if not topics:
        if merge:
            print('Term extraction on the combined text from collection is requested.')
            return process(get_text(texts))
        elif isinstance(texts, WikiArticles):
            topics = [t['name'] for t in texts.list_themes()]
        elif type(texts) is dict:
            topics = list(texts.keys())
        else:
            print('Multiple texts without topic labels are present.')
            print('Term extraction will process the combined texts.')
            return process(get_text(texts))
    
    dfs = dict()
    print('\nProcessing each topic ::>')
    for topic in topics:
        print('\nTopic = {}'.format(topic))
        text = get_text(texts, topic)
        if not text: continue
        df = process(text, prefix = topic)
        dfs[topic] = df
    dfsl = list()
    for t,df in dfs.items():
        dfsl.append(pandas_rename_cols(df, prefix = t))
    DF = pandas_merge_dfs(dfsl)
    if export: export_as_csv(DF)
    return DF