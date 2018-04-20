smartanno_config = '''{
  "setup_instruction":"if there is no 'smartanno_conf.json' under 'conf' directory, need to copy this file and rename it to 'smartanno_conf.json'. ",
  "api_key": "",
  "api_key_comment": "api key for UMLS access",
  "db_header": "sqlite+pysqlite:///",
  "db_path": "data/demo.sqlite",
  "learning_steps": 10,
  "learning_steps_comment": "reclassify the rest of samples after review every # of samples",
  "status": {
    "default": 0,
    "workflow1": 1,
    "workflow_0": 17,
    "tasknamer_2": "task1",
    "types_6": [
      "Typea",
      "Typeb"
    ],
    "tasknamer_5": "task1",
    "tasknamer_6": "task1",
    "tasknamer_25": "task1",
    "types_29": [
      "Typea",
      "Typeb"
    ],
    "umls_extender_loop": 10,
    "w_e_extender_loop": 12,
    "rb_review_loop": 17
  },
  "glove": {
    "vocab": 1900000,
    "vector": 300,
    "model_path": "models/saved/glove/glove.42B.300d.bin"
  },
  "rush_rules_path": "conf/rush_rules.tsv",
  "umls": {
    "sources": [
      "SNOMEDCT_US"
    ],
    "filter_by_length": 0,
    "filter_by_contains": true,
    "max_query": 50
  },
  "review": {
    "review_comment": "configurations of sample data reviewing window",
    "div_height": "200px",
    "div_height_comment": "height of textarea to display the sample",
    "meta_columns": [
      "DOC_ID",
      "DATE",
      "REF_DATE"
    ],
    "rb_model_threshold": 30,
    "rb_model_threshold_comment": "max_documents_for_rb_model",
    "show_meta_name": true,
    "ml_learning_pace": 5,
    "highlight_color": "PaleGreen"
  },
  "cnn_model": {
    "max_token_per_sentence": 5000,
    "stopwords_file": "",
    "learning_pace": 10
  },
  "nb_model": {
    "learning_pace": 10
  },
  "logisticbow_model": {
    "learning_pace": 10
  },
  "whoosh": {
    "root_path": "data/whoosh_idx"
  }
}'''

rush_rules = '''#/*******************************************************************************
# * Copyright  2016  Department of Biomedical Informatics, University of Utah
# * <p>
# * Licensed under the Apache License, Version 2.0 (the "License");
# * you may not use this file except in compliance with the License.
# * You may obtain a copy of the License at
# * <p>
# * http://www.apache.org/licenses/LICENSE-2.0
# * <p>
# * Unless required by applicable law or agreed to in writing, software
# * distributed under the License is distributed on an "AS IS" BASIS,
# * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# * See the License for the specific language governing permissions and
# * limitations under the License.
# *******************************************************************************/

#this list is optimized for shorter rule length rules for semeval were added
@maxRepeatLength:100

#stbegin is the marker for sentence begin, the span of sentence will start at the begin of the captured group
#stbegin has two scores 0, 1: 0 for true sentence begin, 1 for false sentence begin which will overwrite 0 when they are overlapping
#stend is the marker for sentence begin, the span of sentence will end at the end of the captured group
#stend has two scores 2, 3: 2 for true sentence end, 3 for false sentence end which will overwrite 2 when they are overlapping

# \d   A digit
# \C   A capital letter
# \c   A lowercase letter
# \s   A whitespace
# \a   A Non-whitespace character
# \\u   A unusual character: not a letter, not a number, not a punctuation, not a whitespace
# \n   A return
# (   Beginning of capturing a group
# )   End of capturing a group
# \p   A punctuation
# <p>
# \+   An addition symbol (to distinguish the "+" after a wildcard)
# \(   A left parentheses symbol
# \)   A right parentheses symbol
# <p>
# The wildcard plus "+": 1 or more wildcard

\b(\a	0	stbegin
\b(\d	0	stbegin
\b\w+(\a	0	stbegin
\c.\s+(\C)	0	stbegin
 mL.\s+(\C)	0	stbegin
*)	1	stbegin
\c\c.\s+(\C)	0	stbegin
\c\).\s+(\C)	0	stbegin
\d\).\s+(\C)	0	stbegin
\C\C\C.\s+(\C)\c	0	stbegin
\d.\s+(\C)	0	stbegin
\n\n\s+(\C)	0	stbegin
 Med\n\n\n+(\c+)	0	stbegin
 Med\s+\n\n\n+\s+(\c+)	0	stbegin
 Med\s+\n+\s+\n+\s+(\c+)	0	stbegin
 Normal\s+\n+\s+\n+\s+(\c+)	0	stbegin
\c\c.\n+(\c\c	0	stbegin
\c\c.\n+(\d+	0	stbegin
\d%.\n+(\d+	0	stbegin
\c\c.\n\n\w+(\c+)	0	stbegin
\c\c.\s+\n\n\w+(\c+)	0	stbegin
\c\c.\s+\n\n\w+(\c+)	0	stbegin
\c\c.\n\w+(\c+)	0	stbegin
\c\c.\w+(\c+)	0	stbegin
\c.\n+(\d+)\s	0	stbegin
\c.\s+\n+(\d+)\s	0	stbegin
\c.\n+\s+(\d+)\s	0	stbegin
\c.\s+\n+(\d).\s+\d	0	stbegin
\c.\s+\n+\s+(\d+)\s+	0	stbegin
\c.\n+(\d+).\d+x	0	stbegin
\c.\s+\n+(\d+).\d+x	0	stbegin
\c.\n+\s+(\d+).\d+x	0	stbegin
\c.\s+\n+\s+(\d+).\d+x	0	stbegin
\c.\n+(\d+).\d+*	0	stbegin
\c.\s+\n+(\d+).\d+*	0	stbegin
\c.\n+\s+(\d+).\d+*	0	stbegin
\c.\s+\n+\s+(\d+).\d+*	0	stbegin
\c.\n+(\d+)x	0	stbegin
\c.\s+\n+(\d+)x	0	stbegin
\c.\n+\s+(\d+)x	0	stbegin
\c.\s+\n+\s+(\d+)x	0	stbegin
\c.\n+(\d+)\s+\c	0	stbegin
\c.\s+\n+(\d+)\s+\c	0	stbegin
\c.\n+\s+(\d+)\s+\c	0	stbegin
\c.\s+\n+\s+(\d+)\s+\c	0	stbegin
\c.\n+(\d+)\c	0	stbegin
\c.\s+\n+(\d+)\c	0	stbegin
\c.\n+\s+(\d+)\c	0	stbegin
\c.\s+\n+\s+(\d+)\c	0	stbegin
\n\n\s\w+\d+.(\C)	0	stbegin
\n\n\s\w+\d+.\s+(\C)	0	stbegin
\n\n\s\w+(\d)\s	0	stbegin
\n\n\s\w+(\d+)\s	0	stbegin
\n\n\s\w+(")\C	0	stbegin
\n\n\d+.(\C)	0	stbegin
\n\d/\s+(\C)	0	stbegin
\n\n(\d+.\s+\C	0	stbegin
\n(\d+.\s+\c	0	stbegin
\n\n(\d)\s	0	stbegin
\n\n(\d+)\s	0	stbegin
\n\n(")\C	0	stbegin
\n\n(")\s+\C	0	stbegin
\n\n\s+(")\s+\C	0	stbegin
\n\n(-\C	0	stbegin
\n(-\C	0	stbegin
\c.\s+\n(-\C	0	stbegin
\c:\s+\n(-\C	0	stbegin
\c.\n(-\C	0	stbegin
\c:\n(-\C	0	stbegin
\n\n\s+(-\C	0	stbegin
\n\n\s+(-\s+\C	0	stbegin
\n\n(-\s+\C	0	stbegin


\n\n(-\s+\c)\c	0	stbegin
\n\n\s+-\s+(\c)\c	0	stbegin
\c.\n(-\c)\c	0	stbegin
\c:\n(-\c)\c	0	stbegin
\c.\s+\n(-\c)	0	stbegin
\c:\s+\n(-\c)	0	stbegin
\n(-\c)\c	0	stbegin
\n (•  \c	0	stbegin

\c.\n+(-\d)	0	stbegin
\c.\s+\n+(-\d)	0	stbegin
\c.\s+\n+\s+(-\d)	0	stbegin

\n\n*(\C)	0	stbegin
\n\n\s+(*)\C	0	stbegin
\n\n\s+(*)\s+\C	0	stbegin
\n\n(*)\s+\C	0	stbegin
\n\n\s+(')\C	0	stbegin
\n\n(')\C	0	stbegin
\n\n(')\s+\C	0	stbegin
\n\n\s+(')\s+\C	0	stbegin
\n\n\s+(%)\C	0	stbegin
\n\n(%)\C	0	stbegin
\n\n(%)\s+\C	0	stbegin
\n\n\s+(%)\s+\C	0	stbegin
\b*\p+(\C)	0	stbegin
\b\n*\p+(\C	0	stbegin
\n\n*\p+(\C	0	stbegin
\n\n*\p+\s+(\C	0	stbegin
\n**\p+\s+(\C	0	stbegin
\n**\s+(\C	0	stbegin
\n**\p+(\C	0	stbegin
\n**(\C	0	stbegin
\n**(\d	0	stbegin
\n\n\s+*\p+(\C	0	stbegin
\n\n\s+*\p+\s+\C	0	stbegin
\c.\s+**\p+(\C	0	stbegin

\n\n\s+(\u)\s+\d\s	0	stbegin
\n\n\s+(\u)\s+\d+\s	0	stbegin
\n\n\s+(\u)\s+\d+/	0	stbegin
\n\n\s+(\u)\s+\d/	0	stbegin
\n\n\s+(\u)\s+\c	0	stbegin
\n\n\s+(\u)\s+\C	0	stbegin
\n\n(\u)\s+\C	0	stbegin
?\s+(\C)\c	0	stbegin
?\s+(\d	0	stbegin
!\s+(\C)\c	0	stbegin
!\s+(\d	0	stbegin



#start with time
\n\n(\d):\d\s	0	stbegin
\n\n(\d):\d\d\s	0	stbegin
\n\n(\d)\d:\d\d\s	0	stbegin
\n\n(\d)\d:\d\s	0	stbegin
\n\n(\d):\d-	0	stbegin
\n\n(\d):\d\d-	0	stbegin
\n\n(\d)\d:\d\d-	0	stbegin
\n\n(\d)\d:\d-	0	stbegin
\n\n\w+(\d):\d\s	0	stbegin
\n\n\w+(\d):\d\d\s	0	stbegin
\n\n\w+(\d)\d:\d\d\s	0	stbegin
\n\n\w+(\d)\d:\d\s	0	stbegin
\n\n\w+(\d):\d-	0	stbegin
\n\n\w+(\d):\d\d-	0	stbegin
\n\n\w+(\d)\d:\d\d-	0	stbegin
\n\n\w+(\d)\d:\d-	0	stbegin
#start with dates
\n\n(\d+)\s+	0	stbegin
\n\n(\d)\d/\d/\d\d\d\d	0	stbegin
\n\n(\d)/\d/\d\d\d\d	0	stbegin
\n\n(\d)\d/\d\d/\d\d\d\d	0	stbegin
\n\n(\d)/\d\d/\d\d\d\d	0	stbegin
\n\n(\d)\d/\d/\d\d	0	stbegin
\n\n(\d)/\d/\d\d	0	stbegin
\n\n(\d)\d/\d\d/\d\d	0	stbegin
\n\n(\d)/\d\d/\d\d	0	stbegin
\n\n(\d)\d/\d\s	0	stbegin
\n\n(\d)/\d\s	0	stbegin
\n\n(\d)\d/\d\d\s	0	stbegin
\n\n(\d)/\d\d/\d\s	0	stbegin
\n+\s\s\s\s(\C)	0	stbegin
\n+\s\s\s(\C)	0	stbegin
\n+\s\s(\C)	0	stbegin
\n+(\C)	0	stbegin
.\s+(N)ow 	0	stbegin
.\s+(D)ischarge 	0	stbegin

\n(\(-\)\s+\C	0	stbegin
\n        (\d	0	stbegin
\C:\n+(\d	0	stbegin
\n(\d.\s+)\C	0	stbegin
\n(\d.\C	0	stbegin
\n\s+(\d.\s+\C	0	stbegin
\n\s+(\d\d.\s+\C	0	stbegin
\n\d.\)\s+(\C	0	stbegin
\n\d\d.\)\s+(\C	0	stbegin
\c:\n+(\a	0	stbegin
\s+\s+(\d\)\s+\C	0	stbegin
\s+\s+(\d\d\)\s+\C	0	stbegin
\n)                                    \d\d\)	2	stend

\c:\n+(\d. 	0	stbegin
\d:\n+(\d	0	stbegin

\C:\s+\n+(\d	0	stbegin
\C:\s+\n+(1. 	0	stbegin
\c:\s+\n+(\d	0	stbegin
\d:\s+\n+(\d	0	stbegin
\).\s+(\C	0	stbegin
\n(- \c	0	stbegin
\n(- \C	0	stbegin
\n(# \c	0	stbegin
\n(# \C	0	stbegin
\n(#\C	0	stbegin
\n(#\c	0	stbegin
\n(* \c	0	stbegin
\n(* \C	0	stbegin
\n(? \C	0	stbegin
\n(? \c	0	stbegin
\n(. \C	0	stbegin
\n(+ \C	0	stbegin
\n(/ \C	0	stbegin
\n+\d\d-\d\d\s+(\C	0	stbegin
\n+\d+-\d\d-\d\d\s+(\C	0	stbegin
\n+\d+-\d\d-\d\d\s+:\s+(\C	0	stbegin
\c.\s+\n(\d.\C	0	stbegin
\n(\d\)\s+\C	0	stbegin
\n(\d\d\)\s+\C	0	stbegin
\n(\d\)\s+\c	0	stbegin
\n(\d\)\s+?\c	0	stbegin
\n(\d\d\)\s+\c	0	stbegin
\n(\d\)\C	0	stbegin
\s\s(\d\)\C	0	stbegin
\s\s(\d\)?\s+\C	0	stbegin

\c)\w+\d\)\s+\d+\s+(\c	0	stbegin

\c\w+(\d\)\C	0	stbegin
\d\)\C+\w+(\d\)\c	0	stbegin

\c)\w+\d\)	2	stend
\c)\w+\d\d\)	2	stend
\(\a+\w+\a+\)	3	stend
\c\c)\w+\d\d\),	3	stend
\c\c)\w+\d\),	3	stend
\c\c)\w+\d\).	3	stend
\c\c)\w+\d\d\).	3	stend
from \d+ to \d+	3	stend

\C\C)\w+\d\d\),	3	stend
\C\C)\w+\d\),	3	stend
\C\C)\w+\d\).	3	stend
\C\C)\w+\d\d\).	3	stend

\C(\C)\w+\d\)	2	stend
\C(\C)\w+\d\d\)	2	stend
\(\C+\s+\d\d\)	3	stend
\(\c+\s+\d\d\)	3	stend
\d(%)\w+\d\)	2	stend
\d(%)\w+\d\d\)	2	stend
\d)\w+\d\)	2	stend
\d)\w+\d\d\)	2	stend
\d\d-\d\d\s+(.)\s+\C	2	stend
\d\d-\d\d\s+.\s+(\C	0	stbegin
\d\d\d(\d)\s+.\s+\C	2	stend
\d\d\d\d\s+.\s+(\C	0	stbegin

\n(\d.\)\C	0	stbegin
\n(\d.\)\s+\C	0	stbegin
\n\s+(\d.\s+\C	0	stbegin
\n\s+(\d.\)\C	0	stbegin
\n\s+(\d.\)\s+\C	0	stbegin
\n\d.\s+(\d)\d-\d\d\s	0	stbegin
\n\d.\s+(\d)\d-\d\d\d\d\s	0	stbegin
\n\d.\s+(\d)\d-\d\d-\d\d\d\d\s	0	stbegin
\n\(a\)\s+(\C	0	stbegin
\n\(b\)\s+(\C	0	stbegin
\n\(c\)\s+(\C	0	stbegin
\n\(d\)\s+(\C	0	stbegin
\n\(e\)\s+(\C	0	stbegin
\n\(f\)\s+(\C	0	stbegin
\n\(g\)\s+(\C	0	stbegin
\n(\(\d\)\s+\C	0	stbegin
\n("\C	0	stbegin

\a.\s+(This 	0	stbegin
\a.\s+(That 	0	stbegin
\a.\s+(The 	0	stbegin
\a.\s+(She 	0	stbegin
\a.\s+(He 	0	stbegin
\a.\s+(Her 	0	stbegin
\a.\s+(His 	0	stbegin
\a.\s+(They 	0	stbegin
\a.\s+(Their 	0	stbegin
\a.\s+(But 	0	stbegin
\a.\s+(Now 	0	stbegin
\a.\s+(Discharge 	0	stbegin


(\a)\s+\n+-	2	stend
\c(\c)\n+ \C	2	stend
\a(.)\s+This 	2	stend
\a(.)\s+That 	2	stend
\a(.)\s+The 	2	stend
\a(.)\s+She 	2	stend
\a(.)\s+He 	2	stend
\a(.)\s+Her 	2	stend
\a(.)\s+His 	2	stend
\a(.)\s+They 	2	stend
\a(.)\s+Their 	2	stend
\a(.)\s+But 	2	stend
\a(.)\s+Now 	2	stend
\a(.)\s+Discharge 	2	stend
 mL(.)\s+The 	2	stend
\c(.)\s+I	2	stend
\d(.)\s+\C	2	stend
\d(.)\s\C	2	stend
.\s+\d.\s+\C	2	stend
\)(.)\s+\C	2	stend
\p\p\p\s+\n\C	2	stend
\)(.)\s+\n\C	2	stend
\c(\c)\n+\C	2	stend
\c(\c)\s+\n+\C	2	stend
\a\s+\n\n	2	stend
\a\n\n	2	stend
\a\n\e	2	stend
\a\s+\n\e	2	stend
\a\n\n\e	2	stend
\c)********	2	stend
\c)**\n	2	stend
\c)**\s+\n	2	stend
\c)**\p+\s+\n	2	stend
\c)**\p+\n	2	stend
\c)\s+**\p+\s+\n	2	stend
\c\s+**\p+\n	2	stend
\c\s+\n\w+**	2	stend
\c.\s+\n\w+**	2	stend
\d(.)\s+\n\w+**	2	stend
(\d)**\p+\s+\n	2	stend
\d**\p+\n	2	stend
.\s+**\p+\s+\n	2	stend
.\s+**\p+\n	2	stend
.**\p+\s+\n	2	stend
.**\s+\p+\n	2	stend
.**\p+\s+\p+\n	2	stend
.**\p+\n	2	stend
.**\s+\n\n	2	stend
.**\n\n	2	stend
.\s+**\s+\n\n	2	stend
.\s+**\n\n	2	stend
:**\p+\n	2	stend
:**\s+\n\n	2	stend
:**\s+\n\w+	2	stend
:**\n\n	2	stend
:\s+**\s+\n\n	2	stend
:\s+**\n\n	2	stend
:)\n\u\s+\C	2	stend
\d**\s+\n\n	2	stend
\d**\n\n	2	stend
\a\s+\n+**	2	stend
\a\s+\n\w+**\p+\C	2	stend
\c(.\s+**\p+\C	2	stend
\d)\s+\n+\d.\s+\C	2	stend
\d)\s+\n+\d\d.\s+\C	2	stend
\c)\s+\n+\d.\s+\C	2	stend
\c)\s+\n+\d\d.\s+\C	2	stend
\C)\s+\n+\d.\s+\C	2	stend
\C)\s+\n+\d\d.\s+\C	2	stend
\d)\s+\n+\d.\s+\c	2	stend
\c)\s+\n+\d.\s+\c	2	stend
\c)\s+\n+\d\d.\s+\c	2	stend
\C)\s+\n+\d.\s+\c	2	stend
\C)\s+\n+\d\d.\s+\c	2	stend

\c(\))\s+\n\n	2	stend
\c(\c)\s+\n\e	2	stend
\c\c(.)\s+\C	2	stend
\c(.)\s+\e	2	stend
\c(.)\s+\n\e	2	stend
\c(.)\s+\n	2	stend
\d(.)\n	2	stend
\c(:)\n	2	stend
\C(:)\n	2	stend
\d(:)\n	2	stend
\c(:)\s+\n	2	stend
\C(:)\s+\n	2	stend
\d(:)\s+\n	2	stend
\C\C\C(.)\s+\C\c	2	stend
\C(.)\n	2	stend
\)(.)\n	2	stend
](.)\n	2	stend
\c(.)\n	2	stend
\c(.)\e	2	stend
\c\e	2	stend
\C\e	2	stend
\d\e	2	stend
\p\e	2	stend
\c\s+\e	2	stend
\C\s+\e	2	stend
\p\s+\e	2	stend
\d\s+\e	2	stend

\b\d(.)\s+\C	3	stend
\n\d+(.)\s+\C	3	stend
\d+.\C+(:)\s+\n	3	stend
Mrs(.) 	3	stend
Miss(.) 	3	stend
Mr(.) 	3	stend
Ms(.) 	3	stend
\c\n+\c	3	stend
\c\n+\s+\c	3	stend
\c\s+\n+\c	3	stend
\c\s+\n+\s+\c	3	stend

,\w+\c\c	3	stend
,\n\w+\c\c	3	stend
,\w+\c\c	3	stend
,\w+\d+ 	3	stend
,\n\w+\d+ 	3	stend
,\w+\d+ 	3	stend
;\w+\c\c	3	stend

\)\w+\c\c	3	stend
\)\n\w+\c\c	3	stend
\)\w+\d 	3	stend
\)\n\w+\d+ 	3	stend
\)\w+\d 	3	stend
\c)\s+\d+\)\s+\d+\s+.	2	stend
\d+\s+.\s+(\C	0	stbegin

\s+\C(\C)\w+\c\c	3	stend
\s+\C\C(\C)\w+\c\c	3	stend
\s+\C\C\C(\C)\w+\c\c	3	stend

A\w+\c\c	3	stend
A\n\w+\c\c	3	stend
A\w+\c\c	3	stend
A\w+\d+ 	3	stend
A\n\w+\d+ 	3	stend
A\w+\d+ 	3	stend

\d+)\w+week	3	stend
\d+)\w+month	3	stend
\d+)\w+\day	3	stend
\d+)\w+year	3	stend
\d+)\w+cm 	3	stend
\d+)\w+m 	3	stend
\d+)\w+mg 	3	stend
\d+)\w+g 	3	stend
\d+)\w+kg 	3	stend
\d+)\w+lb 	3	stend
\d+)\w+feet 	3	stend
\d+)\w+inch 	3	stend
\d+)\w+ml 	3	stend
\d+)\w+ou 	3	stend
\d+)\w+ounce 	3	stend
\d+)\w+total dose	3	stend
\d+)\w+dose	3	stend
\d+)\w+tablet	3	stend

#start with number + units
\c\n+\d+\s+\c\c	3	stend
\c\n+\s+\d+\s+\c\c	3	stend
\c\s+\n+\d+\s+\c\c	3	stend
\c\s+\n+\d+\s+\s+\c\c	3	stend
#start with float + units
\c\n+\d+.\d+\s+\c\c	3	stend
\c\n+\s+\d+.\d+\s+\c\c	3	stend
\c\s+\n+\d+.\d+\s+\c\c	3	stend
\c\s+\n+\d+.\d+\s+\s+\c\c	3	stend

are:\s+\n+\c	3	stend
\sis:\s+\n+\c	3	stend
was:\s+\n+\c	3	stend
were:\s+\n+\c	3	stend
are:\n+\c	3	stend
\sis:\n+\c	3	stend
was:\n+\c	3	stend
were:\n+\c	3	stend
are:\n+\s+\c	3	stend
\sis:\n+\s+\c	3	stend
was:\n+\s+\c	3	stend
were:\n+\s+\c	3	stend
are:\s+\n+\s+\c	3	stend
\sis:\s+\n+\s+\c	3	stend
was:\s+\n+\s+\c	3	stend
were:\s+\n+\s+\c	3	stend
#:\n+\c)+	3	stend
#:\s+\n+\c\c	3	stend
#:\n+\s+\c\c	3	stend
#:\s+\n+\s+\c\c	3	stend
\spulm.	3	stend

 mL\n+\c)+	3	stend
 mL\s+\n+\c\c	3	stend
 mL\n+\s+\c\c	3	stend
 mL\s+\n+\s+\c\c	3	stend


 \n\n\n+ •  	2	stend
\s+\n\n+\s+\C	2	stend
\d+.\s+\C+(:\s+\n\n+\s+\C\c+\s+\d+.	3	stend
\d+.\s+\C\c+(:\s+\n\n+\s+\C\c+\s+\d+.	3	stend
\a\w+_______________	2	stend
\a(\p)\w+_______________	2	stend
(\c)\n- \c	2	stend
(\c)\n- \C	2	stend
\c.(")\s+\C	2	stend
\c."\s+(\C	0	stbegin

Heart\nFailure	3	stend
 and\s+\n\n	3	stend
 that\s+\n\n	3	stend
 for\s+\n+	3	stend
 had\s+\n+	3	stend
 have\s+\n+	3	stend
 has\s+\n+	3	stend
 "I\s+\n\n	3	stend
 I\s+\n\n	3	stend
\(\C+\s+\n\n	3	stend
\(\c+\s+\n\n	3	stend
\n(rhabdomyolysis:\n	0	stbegin
.\s+\n+(\c+\s+\c+\s+\c+\s+\c+:\n	0	stbegin
.\s+\n+(\c+\s+\c+\s+\c+:\n	0	stbegin
.\s+\n+(\c+\s+\c+\s+\c+:\n	0	stbegin
#\w+(H)istory of Present Illness:	0	stbegin
\c)\w+History of Present Illness:	2	stend
\C)\w+History of Present Illness:	2	stend
\p)\w+History of Present Illness:	2	stend
\c)\w+History of present illness:	2	stend
\C)\w+History of present illness:	2	stend
\p)\w+History of present illness:	2	stend
\c)\w+HISTORY OF PRESENT ILLNESS:	2	stend
\C)\w+HISTORY OF PRESENT ILLNESS:	2	stend
\p)\w+HISTORY OF PRESENT ILLNESS:	2	stend
\c)\w+Past Medical History:	2	stend
\C)\w+Past Medical History:	2	stend
\p)\w+Past Medical History:	2	stend
\c)\w+History of Past Illness:	2	stend
\C)\w+History of Past Illness:	2	stend
\p)\w+History of Past Illness:	2	stend
\c)\w+Chief Complaint:	2	stend
\C)\w+Chief Complaint:	2	stend
\p)\w+Chief Complaint:	2	stend
\c)\w+Chief Complaint:	2	stend
\C)\w+Chief Complaint:	2	stend
\p)\w+Chief Complaint:	2	stend
.)\s+The	2	stend
.\s+(The	0	stbegin
.\s+(\d.\s+\C	0	stbegin
.\s+(\d.\C	0	stbegin
\c(.\s+\d.\C	2	stend


\c)\w+REASON FOR	2	stend
\C)\w+REASON FOR	2	stend
\d)\w+REASON FOR	2	stend
\p)\w+REASON FOR	2	stend
\c)\w+\w+REASON FOR	2	stend
\C)\w+\w+REASON FOR	2	stend
\d)\w+\w+REASON FOR	2	stend
\p)\w+\w+REASON FOR	2	stend
\c)\w+Reason For	2	stend
\C)\w+Reason For	2	stend
\d)\w+Reason For	2	stend
\p)\w+Reason For	2	stend
\c)\w+\w+Reason For	2	stend
\C)\w+\w+Reason For	2	stend
\d)\w+\w+Reason For	2	stend
\p)\w+\w+Reason For	2	stend
R)EASON FOR	0	stbegin
#REASON FOR THIS EXAMINATION(:	2	stend
#REASON FOR\w+(\d	0	stbegin
#REASON FOR\w+(\C	0	stbegin
#REASON FOR\w+(\c	0	stbegin
#REASON FOR\w+(\p	0	stbegin
#Reason For This Examination(:	2	stend
#Reason For\w+(\d	0	stbegin
#Reason For\w+(\C	0	stbegin
#Reason For\w+(\c	0	stbegin
#Reason For\w+(\p	0	stbegin


\c)\w+INDICATION:	2	stend
\C)\w+INDICATION:	2	stend
\d)\w+INDICATION:	2	stend
\p)\w+INDICATION:	2	stend
\c)\w+Indication:	2	stend
\C)\w+Indication:	2	stend
\d)\w+Indication:	2	stend
\p)\w+Indication:	2	stend
#INDICATION(:	2	stend
#INDICATION:\w+(\d	0	stbegin
#INDICATION:\w+(\C	0	stbegin
#INDICATION:\w+(\c	0	stbegin
#INDICATION:\w+(\p	0	stbegin
#Indication(:	2	stend
#Indication:\w+(\d	0	stbegin
#Indication:\w+(\C	0	stbegin
#Indication:\w+(\c	0	stbegin
#Indication:\w+(\p	0	stbegin


\c)\w+REASON:	2	stend
\C)\w+REASON:	2	stend
\d)\w+REASON:	2	stend
\p)\w+REASON:	2	stend
\c)\w+Reason:	2	stend
\C)\w+Reason:	2	stend
\d)\w+Reason:	2	stend
\p)\w+Reason:	2	stend
#REASON(:	2	stend
#REASON:\w+(\d	0	stbegin
#REASON:\w+(\C	0	stbegin
#REASON:\w+(\c	0	stbegin
#REASON:\w+(\p	0	stbegin
#Reason(:	2	stend
#Reason:\w+(\d	0	stbegin
#Reason:\w+(\C	0	stbegin
#Reason:\w+(\c	0	stbegin
#Reason:\w+(\p	0	stbegin

\a)\w+Admitting Diagnosis:	2	stend
\a)\w+ADMITTING DIAGNOSIS:	2	stend
\a\w+(A)dmitting Diagnosis:	0	stbegin
\a\w+(A)DMITTING DIAGNOSIS:	0	stbegin
#Admitting Diagnosis(:	2	stend
#Admitting Diagnosis:\w+(\d	0	stbegin
#Admitting Diagnosis:\w+(\C	0	stbegin
#Admitting Diagnosis:\w+(\c	0	stbegin
#Admitting Diagnosis:\w+(\p	0	stbegin
#ADMITTING DIAGNOSIS(:	2	stend
#ADMITTING DIAGNOSIS:\w+(\d	0	stbegin
#ADMITTING DIAGNOSIS:\w+(\C	0	stbegin
#ADMITTING DIAGNOSIS:\w+(\c	0	stbegin
#ADMITTING DIAGNOSIS:\w+(\p	0	stbegin


\c)\w+Discharge Diagnosis:	2	stend
\d)\w+Discharge Diagnosis:	2	stend
\p)\w+Discharge Diagnosis:	2	stend
\C)\w+Discharge Diagnosis:	2	stend
\c)\w+DISCHARGE DIAGNOSIS:	2	stend
\C)\w+DISCHARGE DIAGNOSIS:	2	stend
\d)\w+DISCHARGE DIAGNOSIS:	2	stend
\p)\w+DISCHARGE DIAGNOSIS:	2	stend
#Discharge Diagnosis(:	2	stend
#Discharge Diagnosis:\w+(\d	0	stbegin
#Discharge Diagnosis:\w+(\C	0	stbegin
#Discharge Diagnosis:\w+(\c	0	stbegin
#Discharge Diagnosis:\w+(\p	0	stbegin
#DISCHARGE DIAGNOSIS(:	2	stend
#DISCHARGE DIAGNOSIS:\w+(\d	0	stbegin
#DISCHARGE DIAGNOSIS:\w+(\C	0	stbegin
#DISCHARGE DIAGNOSIS:\w+(\c	0	stbegin
#DISCHARGE DIAGNOSIS:\w+(\p	0	stbegin

\c)\w+FINDINGS:	2	stend
\C)\w+FINDINGS:	2	stend
\d)\w+FINDINGS:	2	stend
\p)\w+FINDINGS:	2	stend
F)INDINGS:	0	stbegin
#FINDINGS(:	2	stend
#FINDINGS:\w+(\d	0	stbegin
#FINDINGS:\w+(\C	0	stbegin
#FINDINGS:\w+(\c	0	stbegin
#FINDINGS:\w+(\p	0	stbegin
\c)\w+Findings:	2	stend
\C)\w+Findings:	2	stend
\d)\w+Findings:	2	stend
\p)\w+Findings:	2	stend
#Findings(:	2	stend
#Findings:\w+(\d	0	stbegin
#Findings:\w+(\C	0	stbegin
#Findings:\w+(\c	0	stbegin
#Findings:\w+(\p	0	stbegin


#Brief Hospital Course(:	2	stend
#Brief Hospital Course:\w+(\d	0	stbegin
#Brief Hospital Course:\w+(\C	0	stbegin
#Brief Hospital Course:\w+(\c	0	stbegin
#Brief Hospital Course:\w+(\p	0	stbegin




\c(?)\w+	2	stend
\C(?)\w+	2	stend
\d(?)\w+	2	stend
:\w+(?\w+	3	stend


D(.)\s+\n+\d+.\s+\C	2	stend
N(.)\s+\n+\d+.\s+\C	2	stend
NPO(.)\s+\n+\C	2	stend
\)(.)\w+\d+.\s+\C	2	stend
\c+\s+(.)\s+\C\c+	2	stend
\c+\s+.\s+(\C\c+	0	stbegin
P(M\n\C	2	stend
\a)\s\s\s\s+Reason:	2	stend
\s\s\s\s+(Reason:	0	stbegin
\a)\s\s\s\s+Admitting Diagnosis:	2	stend
\s\s\s\s+(Admitting Diagnosis:	0	stbegin
\a)\s\s\s\s+Sex:	2	stend
\s\s\s\s+(Sex:	0	stbegin
\a)\s\s\s\s+Discharge Date:	2	stend
\s\s\s\s+(Discharge Date:	0	stbegin
dail(y\n-	2	stend
qh(s\n-	2	stend
dail(y\n-	2	stend
\sq(d\n-	2	stend
QH(S\n-	2	stend
\a)\s+Refills:	2	stend
\a)*\s+Refills:	2	stend
\a\s+(Refills:	0	stbegin
\a)\n\C:	2	stend
\a)\s+\n\C:	2	stend
\n(\C:	0	stbegin
\n(JOB#:	0	stbegin
\a)\nJOB#:	2	stend
\a)\s+\nJOB#:	2	stend
\n(Signed\s	0	stbegin
\a)\s\s\s\w+Signed\s	2	stend
\c)\n+Signed\s	2	stend
\d)\n+Signed\s	2	stend
\p)\n+Signed\s	2	stend
\(End of Report	0	stbegin
\a)\w+\(End of Report\)	2	stend
Instructions(:\n+\a	2	stend
Instructions:\n+(\a	0	stbegin
\n+(Follow	0	stbegin
\a)\w+\n+Follow	2	stend
\d+\s+\n+total dose	3	stend
\a)\n+\C\c+:	2	stend
\a\n+(\C\c+:	0	stbegin
\a)\n+\C\C+:	2	stend
\a\n+(\C\C+:	0	stbegin
\a)\s+\n+\C\C+:	2	stend
\a\s+\n+(\C\C+:	0	stbegin

\c)\n+\C\C+\s\(\a\a+\):	2	stend
\c\n+(\C\C+\s\(\a\a+\):	0	stbegin
\d)\n+\C\C+\s\(\a\a+\):	2	stend
\d\n+(\C\C+\s\(\a\a+\):	0	stbegin

\a)\n+T\s+	2	stend
\a\n+(T)\s+	0	stbegin
\a)\n+P\s+	2	stend
\a\n+(P)\s+	0	stbegin
\a)\n+R\s+	2	stend
\a\n+(R)\s+	0	stbegin
\a)\s+\n+R\s+	2	stend
\a\s+\n+(R)\s+	0	stbegin
\a)\n+BP\s+	2	stend
\a\n+(BP)\s+	0	stbegin
\a)\n+O2\s+	2	stend
\a\n+(O2)\s+	0	stbegin
\a)\w+Sig:\s+	2	stend
\a\w+(Sig:\s+	0	stbegin
\)(.)\s+\n+\d.\s+\c+	2	stend
\).\s+\n+(\d.\s+\c+	0	stbegin
\)(.)\s+\n+\d.\s+\c+	2	stend
\))\s+\n+\d.\s+\c+	2	stend
\)\s+\n+(\d.\s+\c+	0	stbegin
\))\n+\d.\s+\c+	2	stend
\)\n+(\d.\s+\c+	0	stbegin
\a\n+(\d.\s+\C	0	stbegin
\a)\n+\d.\s+\C	2	stend
\a)*\n+\d.\s+\C	2	stend



\a)\n+\d\d\d\d-\d\d-\d\d\s\s\s+	2	stend
\a)*+\n+\d\d\d\d-\d\d-\d\d\s\s\s+	2	stend
\a\n+(\d)\d\d\d-\d\d-\d\d\s\s\s+	0	stbegin
\a)\s+\n+\d\d\d\d-\d\d-\d\d\s\s\s+	2	stend
\a\s+\n+(\d)\d\d\d-\d\d-\d\d\s\s\s+	0	stbegin
\C\C+\n+(\d+.\s+\C	0	stbegin
\C)\n+\d+.\s+\C	2	stend
\d)\n+\C\C+	2	stend

\c)\n+\C\c+\s\(\a\a+\):	2	stend
\c\n+(\C\c+\s\(\a\a+\):	0	stbegin
\d)\n+\C\c+\s\(\a\a+\):	2	stend
\d\n+(\C\c+\s\(\a\a+\):	0	stbegin

\c.\s+(-)\s+\C	0	stbegin
\c(.)\s+-\s+\C	2	stend
\c\s+(-)\s+\C	0	stbegin
\c\s+-\s+\C	2	stend
\C\c+\s+-\s+\C\c+	3	stend
\C\c+(:)\s+\n+\c	2	stend
\C\c+:\s+\n+(\c	0	stbegin
\C\c+:\n+\s+(\c	0	stbegin
\C\c+(:)\n+\c	2	stend
\C\c+:\n+(\c	0	stbegin
\C\C\C:\n+(\c	0	stbegin
\C\C\C\):\n+(\c	0	stbegin
\sand)\s+\n+\C	3	stend
\sand)\s+\n+\c	3	stend
\sand)\n+\C	3	stend
\sand)\n+\c	3	stend



\c(:)\s+\p+\s+\n	2	stend
\s\s\s+(·)\s+\C	0	stbegin
\c)\s\s\s+·\s\C	2	stend
\c)\s\s\s+·\s\C	2	stend
\p)\s\s\s+·\s\C	2	stend
\C\c+\s+(-)\s+\C\c+	1	stbegin
\s\s+(P)atient Name:	0	stbegin
\s\s\s+(P)rocedure Date:	0	stbegin
\s\s\s+(D)ate of Birth:	0	stbegin
\s\s\s+(A)ge:	0	stbegin
\s\s\s+(G)ender:	0	stbegin
\s\s\s+(N)ote Status:	0	stbegin

\a)\s\s+Patient Name:	2	stend
\a)\s\s\s+Procedure Date:	2	stend
\a)\s\s\s+Date of Birth:	2	stend
\a)\s\s\s+Age:	2	stend
\a)\s\s\s+Gender:	2	stend
\a)\s\s\s+Note Status:	2	stend
\n\n(\(\a+	0	stbegin
\c.\n+(\(\a+	0	stbegin
\n+(\c)\c+:	0	stbegin
\a+\)\n\s+\c\c+:	2	stend
\a+\)\s+\n+\c\c+:	2	stend
\a+\)\n+\c\c+:	2	stend
\a+\)\s+\n+\s+\c\c+:	2	stend
\c\n+\c\c+:	2	stend

On)\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend
On)\s+\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend
on)\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend
on)\s+\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend
by)\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend
by)\s+\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend
since)\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend
since)\s+\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend
Since)\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend
Since)\s+\n+\d\d\d\d-\d\d-\d\d\s\s\s+	3	stend

\a)\s+**+\s+\n\n	2	stend
\a)\s+**+\n\n	2	stend

\a(\a)\n+\d\).\s+\C	2	stend
\a\n+\d\)(.)\s+\C	3	stend
\C\C\n+(\d\).\s+\C	0	stbegin
\c.\n+(\d\).\s+\C	0	stbegin
\C\C.\n+(\d\).\s+\C	0	stbegin
\c.\s+\n+(\d)\).\s+\C	0	stbegin
.\s+\n+\d\)(.)\s+\C	3	stend


\a\n+(\d)\d-\d\d\s+	0	stbegin
\a\s+\n+(\d)\d-\d\d\s+	0	stbegin
\a.\s+\n+(\d)\d-\d\d\s+	0	stbegin

\c\w+(\d)\)\s+\C	0	stbegin
\c\c+.\w+(\d)\)\s+\C	0	stbegin
\c+\c(.)\w+\d\)\s+\C	2	stend


\a)\s+\n+\C\c+\s+\C\c+:	2	stend
\a\s+\n+(\C)\c+\s+\C\c+:	0	stbegin
\a)\s+\n+\C\c+:	2	stend
\a\s+\n+(\C)\c+:	0	stbegin
\a)\w+Date of Birth:	2	stend
\w+(D)ate of Birth:	0	stbegin

\c:\s+\n(\a	0	stbegin
\sDr(.)\s	3	stend
\sMr(.)\s	3	stend
\sMrs(.)\s	3	stend
\sMs(.)\s	3	stend
\sth(e)\n\C\c+	3	stend
\sTh(e)\n\C\c+	3	stend
\si(n)\n\a+	3	stend
\sI(n)\n\a+	3	stend
\sfo(r)\n\a+	3	stend
\sb(y)\a+	3	stend
\shi(s)\a+	3	stend
\she(r)\a+	3	stend
\swit(h)\a+	3	stend
\so(n)\a+	3	stend
\sO(n)\a+	3	stend
\sunti(l)\a+	3	stend
\sUnti(l)\a+	3	stend
\so(f)\a+	3	stend
\sthroug(h)\a+	3	stend
\san(d)\a+	3	stend
\so(r)\n\a+	3	stend
\sa(s)\n\a+	3	stend
\sincludin(g)\a+	3	stend


Cardiac\w+Surgery\w+Intensive\w+Care\w+Unit	3	stend
\C\c+\w+Cardiac\w+Surge\(+ry\w+Intensive\w+Care\w+Unit	3	stend
Intensive\w+Care\w+Unit	3	stend
\C\c+\w+Intensive\w+Care\w+Unit	3	stend
Emergency\w+Department	3	stend
Coronary\w+Care\w+Unit	3	stend

\a)*\n\n	2	stend
\a)*\n\d\d+.\s\C	2	stend
\a)*\n\d.\s\C	2	stend

CENTER\w+(.	2	stend
Paterna(l	3	stend
HOSPITAL\w+(.	2	stend
CENTER\w+.\w+(\C	0	stbegin
HOSPITAL\w+.\w+(\C	0	stbegin
\C\c+\w+Surgery	3	stend

\c.\c(.)\w+\C\c\c	2	stend
\wTR(.\w+\C\c\c	2	stend
\wTR.\w+(\C)\c\c	0	stbegin
.)\w+He 	2	stend
.)\w+His 	2	stend
.)\w+Her 	2	stend
.)\w+She 	2	stend
.)\w+We 	2	stend
.)\w+Our 	2	stend
.)\w+The 	2	stend
.)\w+They 	2	stend
.)\w+Their 	2	stend
.)\w+I 	2	stend
.)\w+My 	2	stend

.\w+(He 	0	stbegin
.\w+(His 	0	stbegin
.\w+(Her 	0	stbegin
.\w+(She 	0	stbegin
.\w+(We 	0	stbegin
.\w+(Our 	0	stbegin
.\w+(The 	0	stbegin
.\w+(They 	0	stbegin
.\w+(Their 	0	stbegin
.\w+(I 	0	stbegin
.\w+(My 	0	stbegin


'''
pycontext_rules = '''Comments: ''
Direction: backward
Lex: are ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: be ruled out
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: backward
Lex: being ruled out
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: backward
Lex: can be ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: cannot be excluded
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: backward
Lex: cannot totally be excluded
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: could be ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: free
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: has been ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: have been ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: is in the differential
Regex: is\sin\sthe\sdifferential
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: backward
Lex: is negative
Regex: (is|was) negative
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: is not excluded
Regex: (is|was|are|were)\snot\sexcluded
Type: AMBIVALENT_EXISTENCE
---
Comments: 2/28/2013; added definitely; removed ed
Direction: backward
Lex: is not entirely excluded
Regex: (is|was|are|were|does)\snot\s(entirely|totally|definitely|completely\s) excluded
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: is ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: is to be ruled out
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: backward
Lex: is ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: might be ruled out
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: must be ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: not been ruled out
Regex: ''
Type: INDICATION
---
Comments: 3/22/2013
Direction: backward
Lex: not definitively seen
Regex: not definitively (seen|visualized)
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: not excluded
Regex: not\s(excluded|ruled\sout)
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: backward
Lex: now measuring
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: backward
Lex: ought to be ruled out
Regex: ''
Type: INDICATION
---
Comments: 3/22/2013
Direction: backward
Lex: progressed
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: backward
Lex: protocol
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: backward
Lex: resolved
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: backward
Lex: should be ruled out
Regex: ''
Type: INDICATION
---
Comments: 4/29/2013
Direction: backward
Lex: suspected
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: unlikely
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: varying ages
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: backward
Lex: was ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: backward
Lex: will be ruled out
Regex: ''
Type: INDICATION
---
Comments: 2/28/2013
Direction: backward
Lex: would not be expected
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: acute
Regex: ''
Type: ACUTE
---
Comments: ''
Direction: bidirectional
Lex: again
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: age indeterminate
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: appear
Regex: (\bappear\b|\bappears\b)
Type: PROBABLE_EXISTENCE
---
Comments: 2/28/2013
Direction: bidirectional
Lex: cannot be completely excluded
Regex: cannot\sbe\s((entirely|completely|totally)\s)?(excluded|ruled out)
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: 2/28/2013
Direction: bidirectional
Lex: cannot be evaluated
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: '2/28/2013; chronicity: make regular expression to capture variations'
Direction: bidirectional
Lex: chronic
Regex: \bchronic[a-z]*\b
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: diminished
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: equivocal
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: evaluation
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: bidirectional
Lex: evolving
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: healing
Regex: \b(healing|healed)\b
Type: HISTORICAL
---
Comments: 4/2013
Direction: bidirectional
Lex: improved
Regex: improved|improving|improvement
Type: HISTORICAL
---
Comments: 4/29/2013
Direction: bidirectional
Lex: incompletely evaluated
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: interval change
Regex: ''
Type: HISTORICAL
---
Comments: 4/29/2013
Direction: bidirectional
Lex: interval increase
Regex: (interval)\b[\d\D\s]*increase
Type: HISTORICAL
---
Comments: 4/29/2013
Direction: bidirectional
Lex: less likely
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: likely
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: 2/28/2013; thought of just changing chronic to bidirectional;  but also
  capture likely
Direction: bidirectional
Lex: likely chronic
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: may be ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: new
Regex: ''
Type: ACUTE
---
Comments: ''
Direction: bidirectional
Lex: new from prior exam
Regex: new from(\sthe)? prior (exam|study)
Type: ACUTE
---
Comments: ''
Direction: bidirectional
Lex: no longer noted
Regex: no longer (seen|noted|visualized)
Type: DEFINITE_NEGATED_EXISTENCE

---
Comments: ''
Direction: bidirectional
Lex: not significantly changed
Regex: ''
Type: HISTORICAL
---
Comments: need regular expression
Direction: bidirectional
Lex: on previous exam
Regex: (on |from )?(previous|prior) exam
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: persistent
Regex: ''
Type: HISTORICAL
---
Comments: 2/28/2013
Direction: bidirectional
Lex: possible
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: 3/21/2013; changed to bidirectional
Direction: bidirectional
Lex: previous
Regex: ''
Type: HISTORICAL
---
Comments: 3/21/2013; 3/22/2013
Direction: bidirectional
Lex: previously described
Regex: previously (described|suspected)
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: prior
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: prior study
Regex: ''
Type: HISTORICAL
---
Comments: 3/21/2013
Direction: bidirectional
Lex: probable
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: 4/29/2013
Direction: bidirectional
Lex: questionable
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: ruled out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: should be considered
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: stable
Regex: ''
Type: HISTORICAL
---
Comments: 4/29/2013
Direction: bidirectional
Lex: still evident
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: subacute
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: suggest
Regex: \bsuggest[a-z]+\b
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: unchanged
Regex: unchanged|unchanging
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: versus
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: absence of
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: adequate to rule the patient out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: assessment for
Regex: ''
Type: INDICATION
---
Comments: 4/29/2013
Direction: forward
Lex: at risk for
Regex: (at\s)?risk\s(in\sthe\sfuture\s)?(for|of)
Type: FUTURE
---
Comments: 4/29/2013
Direction: forward
Lex: atypical for
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: be ruled out for
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: can be ruled out for
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: can rule the patient out
Regex: can rule (her|him|the patient) out
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: cannot
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: cannot exclude
Regex: cannot\sexclude
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: cannot see
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: cannot totally exclude
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: change in
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: changing
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: checked for
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: '2/28/2013; simplified expression '
Direction: forward
Lex: clinical concern
Regex: clinical (concern|suspicion)\b
Type: FUTURE
---
Comments: ''
Direction: forward
Lex: clinical history
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: concerning for
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: could be ruled out for
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: declined
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: declines
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: make regular expression to capture variations
Direction: forward
Lex: decrease in
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: decrease in
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: denied
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: denies
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: deny
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: denying
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: did rule (the patient|him|her) out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: did rule out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: differential diagnosis would include
Regex: differential\s((diagnosis|considerations)\s)?((would|could)\sinclud[a-z]*)?
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: documented
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: evaluate for
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: evaluation of
Regex: evaluation\s(of|for)
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: did rule her out against
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: examination for
Regex: (study|exam|examination) for
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: fails to reveal
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: free of
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: gram negative
Regex: ''
Type: PSEUDONEG
---
Comments: 2/28/2013
Direction: forward
Lex: higher sensitivity for
Regex: ''
Type: INDICATION
---
Comments: 2/28/2013
Direction: forward
Lex: if there are
Regex: ''
Type: FUTURE
---
Comments: ''
Direction: forward
Lex: if there is concern for
Regex: ''
Type: FUTURE
---
Comments: ''
Direction: forward
Lex: is to be ruled out for
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: is more sensitive
Regex: is more sensitive
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: known
Regex: \bknown\b
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: low probability
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: 2/28/2013
Direction: forward
Lex: may be related
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: may represent
Regex: (may|might)\s(represent|reflect)
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: might be ruled out for
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: 3/22/2013
Direction: forward
Lex: mimicking
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: must be ruled out for
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: negative examination for
Regex: negative (examination|study|exam|evaluation) for
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: negative for
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: never developed
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: never had
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: 2/28/2013; changed from probable to definite
Direction: forward
Lex: no abnormal
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no cause of
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no complaints of
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no convincing
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no definite
Regex: no[\s]*definite
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: need regular expression
Direction: forward
Lex: no definite change
Regex: ''
Type: HISTORICAL
---
Comments: 2/28/2013; added other probably consider simplifying re as XYZ
Direction: forward
Lex: no evidence of
Regex: (no|without)\s((definite|other|definitive|secondary|indirect)\s)?((radiographic|sonographic|CT)\s)?evidence\s(of|for)
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no findings of
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no findings to indicate
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: 4/16/2013
Direction: forward
Lex: no increase
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: no new
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no obvious
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no other
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no sign of
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no significant
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no significant change
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: no significant interval change
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: no signs
Regex: no sign(s)?
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no definite signs of
Regex: (no|without) (definite|definitive|secondary|indirect) ((radiographic|sonographic|CT)\s)?signs\s(of|for)
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no suggestion
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: 4/16/2013
Direction: forward
Lex: no suspicious change
Regex: ''
Type: HISTORICAL
---
Comments: 2/14/2013
Direction: forward
Lex: no XYZ to suggest
Regex: (\b(without|no)\b[\d\D\s]*to suggest)
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: nor
Regex: \bnor\b
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not appreciate
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not associated with
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not cause
Regex: ''
Type: PSEUDONEG
---
Comments: ''
Direction: forward
Lex: not certain whether
Regex: ''
Type: PSEUDONEG
---
Comments: 3/22/2013
Direction: forward
Lex: not clearly evident
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not complain of
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not demonstrate
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not drain
Regex: ''
Type: PSEUDONEG
---
Comments: ''
Direction: forward
Lex: not exhibit
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not extend
Regex: ''
Type: PSEUDONEG
---
Comments: ''
Direction: forward
Lex: not feel
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not had
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not have
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not know of
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not known to have
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not necessarily
Regex: ''
Type: PSEUDONEG
---
Comments: ''
Direction: forward
Lex: not reveal
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not see
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not to be
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: nothing
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: ought to be ruled out for
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: patient was not
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: 2/14/2013
Direction: forward
Lex: 'predispose to '
Regex: ''
Type: FUTURE
---
Comments: ''
Direction: forward
Lex: progression of
Regex: progression\s(of|in)
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: rather than
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: redemonstration
Regex: (re-demonstrat[a-z]*|redemonstrat[a-z]*)
Type: HISTORICAL
---
Comments: 2/28/2013; added for Ami's 19649
Direction: forward
Lex: remote
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: residual
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: resolution of
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: resolving
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: rule her out
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: rule him out
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: rule him out for
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: rule out
Regex: (r/o|rule out|\br o\b|r\.o\.|\bro\b)
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: rule out for
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: rule patient out for
Regex: rule (him|her|patient|the patient|subject) out for
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: rule the patient out
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: rule the patient out for
Regex: ''
Type: INDICATION
---
Comments: 4/16/2013
Direction: forward
Lex: ruled her out against
Regex: ruled\s(him|her|the subject|the patient|subject|patient)\sout( against| for)?
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: ruled out against
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: ruled out for
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: rules her out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: rules her out for
Regex: rules\s(him|her)\sout\sfor
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: rules him out
Regex: rules\s(him|her)\sout
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: rules him out for
Regex: rules\s(him|her)\sout\sfor
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: rules out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: rules out for
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: rules the patient out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: rules the patient out for
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: sequelae of
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: should be ruled out for
Regex: ''
Type: INDICATION
---
Comments: 3/22/2013
Direction: forward
Lex: simulating
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: study for detection
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: sufficient to rule out
Regex: sufficient\sto\srule\s((her|him|the patient|the subject)\s)?out
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: suspicious
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: suspicous
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: test for
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: to exclude
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: unable to adequately assess
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: unable to assess
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: unremarkable for
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: 3/22/2013
Direction: forward
Lex: warned of
Regex: ''
Type: FUTURE
---
Comments: ''
Direction: forward
Lex: were warned
Regex: ''
Type: FUTURE
---
Comments: ''
Direction: forward
Lex: what must be ruled out is
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: will be ruled out for
Regex: ''
Type: INDICATION
---
Comments: ''
Direction: forward
Lex: with no
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: without
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: without difficulty
Regex: ''
Type: PSEUDONEG
---
Comments: ''
Direction: forward
Lex: without indication
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: without sign
Regex: without sign(s)?
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: worrisome
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: '#NAME?'
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: terminate
Lex: although
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: apart from
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a cause for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a cause of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a etiology for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a etiology of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a reason for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a reason of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary cause for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary cause of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary etiology for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary etiology of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary origin for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary origin of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary reason for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary reason of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary source for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a secondary source of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a source for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as a source of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an cause for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an cause of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an etiology for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an etiology of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an origin for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an origin of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an reason for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an reason of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary cause for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary cause of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary etiology for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary etiology of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary origin for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary origin of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary reason for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary reason of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary source for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an secondary source of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an source for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as an source of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the cause for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the cause of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the etiology for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the etiology of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the origin for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the origin of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the reason for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the reason of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary cause for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary cause of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary etiology for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary etiology of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary origin for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary origin of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary reason for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary reason of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary source for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the secondary source of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the source for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: as the source of
Regex: ''
Type: CONJ
---
Comments: 2/14/2013
Direction: terminate
Lex: 'as there are '
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: aside from
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: but
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: cause for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: cause of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: causes for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: causes of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: etiology for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: etiology of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: except
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: however
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: involving
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: nevertheless
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: origin for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: origin of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: origins for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: origins of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: other possibilities of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: reason for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: reason of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: reasons for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: reasons of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: secondary to
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: source for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: source of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: sources for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: sources of
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: still
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: though
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: trigger event for
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: which
Regex: ''
Type: CONJ
---
Comments: ''
Direction: terminate
Lex: yet
Regex: ''
Type: CONJ
---
Comments: ''
Direction: forward
Lex: (no|nothing) convincing
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: (the patient|him|her) was not
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: as a suggestion
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: associated with
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: borderline
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: can rule out
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: can rule out against
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: can rule out for
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: cannot rule out
Regex: cannot rule (the patient |him |her )?out
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: backward
Lex: completely excluded
Regex: (completely|entirely)? excluded
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: construed as
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: could be
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: could not be ruled
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: could represent
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: equivocal
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: every indication
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: backward
Lex: excluded
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: exhibit
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: highly hesitant
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: indication
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: insufficient to rule (the patient|him|her) out for
Regex: ''
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no other (CT|radiographic|sonographic|MR|etc) evidence
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no secondary (CT|radiographic|sonographic|MR|etc) signs
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: no suspicious
Regex: ''
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not adequate to rule out
Regex: not adequate to rule ((the patient|him|her)\s)?out
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: not likely
Regex: ''
Type: DEFINITE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: not only
Regex: ''
Type: PSEUDONEG
---
Comments: ''
Direction: backward
Lex: seen best
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: bidirectional
Lex: signs of
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: backward
Lex: was not excluded
Regex: (was|were) not excluded
Type: AMBIVALENT_EXISTENCE
---
Comments: ''
Direction: forward
Lex: if
Regex: ''
Type: HYPOTHETICAL
---
Comments: ''
Direction: bidirectional
Lex: decrease
Regex: decrease|decreased|decreasing|reduction|reduced
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: increase
Regex: increase|increasing|increased
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex: possibly
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: decrease the likelihood
Regex: decreas[a-z]+(\sthe)? likelihood
Type: PROBABLE_NEGATED_EXISTENCE
---
Comments: ''
Direction: forward
Lex: suspect
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: likely represents
Regex: likely (represents|representing)
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: backwards
Lex: without change
Regex: ''
Type: HISTORICAL
---
Comments: ''
Direction: bidirectional
Lex: risk factor
Regex: risk factor(s)?
Type: FUTURE
---
Comments: ''
Direction: bidirectional
Lex: favor
Regex: ''
Type: PROBABLE_EXISTENCE
---
Comments: ''
Direction: forward
Lex: aunt's
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: aunt
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: cousin
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: cousin's
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: brother's
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: brothers
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: brother
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: dad's
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: dad
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: daughters
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: daughter
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: 'f/h'
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: fam hx
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: family history
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: family
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: father's
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: father
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: fh
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: grandfather's
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: grandfather
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: grandmother's
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: grandmother
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: mom's
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: mom
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: mother's
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: mother
Regex: ''
Type: FAMILY
---
Comments: ''
Direction: forward
Lex: h/o
Regex: ''
Type: FAMILY

---
Comments: ''
Direction: backward
Lex: years ago
Regex: '\b\d+ years ago'
Type: HISTORICAL
---
Comments: ''
Direction: forward
Lex:  'no'
Regex: 
Type: DEFINITE_NEGATED_EXISTENCE'''
