# coding: utf-8

import os
import logging


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


SERVICE_PORT = 5001


DATA_DIR = 'E:\\tmp\\mlang'

SERVICE_DIR = os.path.join(DATA_DIR, 'service')
SERVICE_TMP_DIR = os.path.join(SERVICE_DIR, 'tmp')
SERVICE_CORPUS_DIR = os.path.join(SERVICE_DIR, 'corpus')
SERVICE_VOCAB_DIR = os.path.join(SERVICE_DIR, 'vocab')
SERVICE_W2V_DIR = os.path.join(SERVICE_DIR, 'w2v')
SERVICE_D2V_DIR = os.path.join(SERVICE_DIR, 'd2v')
SERVICE_LM_DIR = os.path.join(SERVICE_DIR, 'lm')
SERVICE_S2S_DIR = os.path.join(SERVICE_DIR, 'seq2seq')

NLP_DATA_DIR = os.path.join(DATA_DIR, 'nlp')
NLP_POS_DATA_DIR = os.path.join(NLP_DATA_DIR, 'pos')
NLP_LEXICON_DIR = os.path.join(NLP_DATA_DIR, 'lexicons')
NLP_LTP_DATA_DIR = os.path.join(NLP_DATA_DIR, 'ltp', '3.4.0')

IE_SA_EXTRACT_RULE_DIR = os.path.join(DATA_DIR, 'ie', 'sa', 'extract_rule')

MODEL_P2H_DIR = os.path.join(DATA_DIR, 'model', 'p2h')
MODEL_SBD_DIR = os.path.join(DATA_DIR, 'model', 'sbd')

MODEL_LM_DIR = os.path.join(DATA_DIR, 'model', 'lm')
MODEL_LM_BERKELEYLM_DIR = os.path.join(MODEL_LM_DIR, 'berkeleylm')

SEMANTICS_DIR = os.path.join(DATA_DIR, 'semantics')
