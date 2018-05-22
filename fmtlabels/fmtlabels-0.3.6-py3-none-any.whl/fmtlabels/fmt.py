#coding=utf-8

import json
import requests
import time
import os

aspectTypeMap = {
    '包装': 'package',
    '产品': 'product',
}

aspectSubtypeMap = {
}

def fmtjson(category, rows, output):
    data = {}
    for row in rows:
        if not 'review_text' in row:
            continue
        text = row['review_text']
        if not text in data:
            analyzeResult = analyze(category, text)
            data[text] = analyzeResult
        else:
            analyzeResult = data[text]

        if not 're_rating' in row:
            continue

        opkey = row['review_type'] + '.' + \
                row['review_subtype'] + '=' + \
                str(row['review_rating'])
        if opkey in analyzeResult['opinionsMap']:
            op = analyzeResult['opinionsMap'][opkey]
            if 'keyword_err' in row:
                op['aspectError'] = 0 if row['keyword_err'] in [None, '', 0 , '0'] else 1
            if 're_rating' in row:
                op['polarityCheck'] = int(row['re_rating']) if not row['re_rating'] in [None, ''] else op['polarity']
            if 'sentiment_words' in row and 'exclude_words' in row:
                op['suggestion'] = {
                    'addAspectTerms': None,
                    'addOpinionTerms': str(row['sentiment_words']).split(','),
                    'excludeOpinionTerms': str(row['exclude_words']).split(','),
                }
            if 'mark' in row:
                op['mark'] = row['mark']
                if str(row['mark']).find('对比关系') >= 0:
                    op['errType'] = 1006
                elif str(row['mark']).find('垃圾评论') >= 0:
                    op['errType'] = 1005
                elif str(row['mark']).find('错别字') >= 0:
                    op['errType'] = 1007
                elif row['mark'] in [None, '']:
                    if op.get('aspectError',None) == 0 and \
                        op.get('polarity',None) == op.get('polarityCheck', None):
                        op['errType'] = 0

    for (_, record) in data.items():
        for op in record['opinions']:
            op['aspectType'] = op['aspectType'].lower()
            if op['aspectType'] in aspectTypeMap:
                op['aspectType'] = aspectTypeMap[op['aspectType']]
            op['aspectSubtype'] = op['aspectSubtype'].lower()
            if op['aspectSubtype'] in aspectSubtypeMap:
                op['aspectSubtype'] = aspectSubtypeMap[op['aspectSubtype']]
        del record['opinionsMap']
        json.dump(record, output, ensure_ascii=False)
        output.write('\n')

nlpaddr = 'http://40.125.161.9:23210/api/sentiment/analysis' \
    if not 'NLP_ADDR' in os.environ else os.environ['NLP_ADDR']
rs = requests.Session()

def analyze(category, text):
    payload={'category':category,'text':text}
    for retry in [0,1,2]:
        try:
            resp = rs.post(nlpaddr, data=payload, timeout=2)
            rjson = resp.json()
            break
        except:
            time.sleep(1)
            if retry == 2:
                print('analyze failed:', category, text)
                raise
    if rjson['ok'] != True:
        if 'error' in rjson.keys():
            raise Exception(text, rjson['error']['reason'])
        raise Exception(text)

    opinions = []
    opinionsMap = {}
    result = {
        'text': text,
        'opinions': opinions,
        'opinionsMap': opinionsMap,
    }
    for aspect in rjson['data']:
        opinion = {
            'aspectType': aspect['levels'][0],
            'aspectSubtype': aspect['levels'][1],
            'polarity': aspect['review_rating'],
            'aspectTerm': str(aspect['matched_key']).split(','),
            'opinionTerm': aspect['emt_words'],
            'rule': None,
            'aspectError': None,
            'polarityCheck': None,
            'errType': None,
            'suggestion':{},
            'mark': None,
        }
        opinions.append(opinion)
        opinionsMap[opinionKey(opinion)] = opinion
        result['textPolarity'] = aspect['text_emotion']
    return result

def opinionKey(opinion):
    return opinion['aspectType'] + '.' + \
           opinion['aspectSubtype'] + '=' + \
           str(opinion['polarity'])