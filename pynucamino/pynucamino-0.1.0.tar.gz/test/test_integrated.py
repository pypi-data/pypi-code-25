'''Integration test for PyNucamino'''

import json
import unittest

import pynucamino


TEST_FASTA = '''> Test Sequence
GCGCCCATCACGGCGTACGCCCAGCAGACGAGAGGCCTCCTAGGGTGTATAATCACCAGCCTGACTGGCCGGGACAAAA
ACCAAGTGGAGGGTGAGGTCCAGATCGTGTCAACTGCTACCCAAACCTTCCTGGCAACGTGCATCAATGGGGTATGCTG
GACTGTCTACCACGGGGCCGGAACGAGGACCATCGCATCACCCAAGGGTCCTGTCATCCAGATGTATACCAATGTGGAC
CAAGACCTTGTGGGCTGGCCCGCTCCTCAAGGTTCCCGCTCATTGACACCCTGCACCTGCGGCTCCTCGGACCTTTACC
TGGTCACGAGGCACGCCGATGTCATTCCCGTGCGCCGGCGAGGTGATAGCAGGGGTAGCCTGCTTTCGCCCCGGCCCAT
TTCCTACTTGAAAGGCTCCTCGGGGGGTCCGCTGTTGTGCCCCGCGGGACACGCCGTGGGCCTATTCAGGGCCGCGGTG
TGCACCCGTGGAGTGGCTAAGGCGGTGGACTTTATCCCTGTGGAGAACCTAGAGACAACCATGAGATCCCCGGTGTTCA
CGGACAACTCCTCTCCACCAGCAGTGCCCCAGAGCTTCCAGGTGGCCCACCTGCAGGCTCCCACCGGCAGCGGTAAGAG
CACCAAGGTCCCGGCTGCGTACGCAGCCCAGGGCTACAAGGTGTTGGTGCTCGACCCCTCTGTTGCTGCAACGCTGGGC
TTTGGTGCTTACATGTCCAAGGCCCATGGGGTTGATCCTAATATCAGGACCGGGGTGAGAACAATTACCACTGGCAGCC
CCATCACGTACTCCACCTACGGCAAGTTCCTTGCCGACGGCGGGTGCTCAGGAGGTGCTTATGACATAATAATTTGTGA
CGAGTGCCACTCCACGGATGCCACATCCATCTTGGGCATCGGCACTGTCCTTGACCAAGCAGAGACTGCGGGGGCGAGA
CTGGTTGTGCTCGCCACTGCTACCCCTCCGGGCTCCGTCACTGTGTCCCATCCTAACATCGAGGAGGTTGCTCTGTCCA
CCACCGGAGAGATCCCTTTTTACGGCAAGGCTATCCCCCTCGAGGTGATCAAGGGGGGAAGACATCTCATCTTCTGCCA
CTCAAAGAAGAAGTGCGACGAGCTCGCCGCGAAGCTGGCCGCATTGGGCATCAATGCCGTGGCCTACTACCGCGGTCTT
GACGTGTCTGTCATCCCGACCAGCGGCGATGTTGTCGTCGTGTCGACCGATGCTCTCATGACTGGCTTTACCGGCGACT
TCGACTCTGTGATAGACTGCAACACGTGTGTCACTCAGACAGTCGATTTCAGCCTTGACCCTACCTTTACCATTGAGAC
AACCACGCTCCCCCAGGATGCTGTCTCCAGGACTCAACGCCGGGGCAGGACTGGCAGGGGGAAGCCAGGCATCTACAGA
TTTGTGGCACCGGGGGAGCGCCCCTCCGGCATGTTCGACTCGTCCGTCCTCTGTGAGTGCTATGACGCGGGCTGTGCTT
GGTATGAGCTCACGCCCGCCGAGACTACAGTTAGGCTACGAGCGTACATGAACACCCCGGGGCTTCCCGTGTGCCAGGA
CCATCTTGAATTTTGGGAGGGCGTCTTTACGGGCCTCACTCATATAGATGCCCACTTTCTATCCCAGACAAAGCAGAGT
GGGGAGAACTTTCCTTACCTGGTAGCGTACCAAGCCACCGTGTGCGCTAGGGCTCAAGCCCCTCCCCCATCGTGGGACC
AGATGTGGAAGTGTTTGATCCGCCTTAAACCCACCCTCCATGGGCCAACACCCCTGCTATACAGACTGGGCGCTGTTCA
GAATGAAGTCACCCTGACGCACCCAATCACCAAATACATCATGACATGCATGTCGGCCGACCTGGAGGTCGTCACG'''

EXPECTED_OUTPUT = json.loads('''{
  "NS3": [
    {
      "Name": "Test Sequence",
      "Report": {
        "FirstAA": 1,
        "FirstNA": 1,
        "LastAA": 631,
        "LastNA": 1893,
        "Mutations": [
          {
            "Position": 203,
            "NAPosition": 607,
            "CodonText": "CAG",
            "AminoAcidText": "Q",
            "ReferenceText": "H",
            "IsInsertion": false,
            "IsDeletion": false,
            "IsPartial": false,
            "Control": "...",
            "InsertedCodonsText": "",
            "InsertedAminoAcidsText": ""
          },
          {
            "Position": 229,
            "NAPosition": 685,
            "CodonText": "GAC",
            "AminoAcidText": "D",
            "ReferenceText": "N",
            "IsInsertion": false,
            "IsDeletion": false,
            "IsPartial": false,
            "Control": "...",
            "InsertedCodonsText": "",
            "InsertedAminoAcidsText": ""
          },
          {
            "Position": 382,
            "NAPosition": 1144,
            "CodonText": "GCC",
            "AminoAcidText": "A",
            "ReferenceText": "V",
            "IsInsertion": false,
            "IsDeletion": false,
            "IsPartial": false,
            "Control": "...",
            "InsertedCodonsText": "",
            "InsertedAminoAcidsText": ""
          }
        ],
        "FrameShifts": [],
        "AlignedSites": [
          {
            "PosAA": 1,
            "PosNA": 1,
            "LengthNA": 3
          },
          {
            "PosAA": 2,
            "PosNA": 4,
            "LengthNA": 3
          },
          {
            "PosAA": 3,
            "PosNA": 7,
            "LengthNA": 3
          },
          {
            "PosAA": 4,
            "PosNA": 10,
            "LengthNA": 3
          },
          {
            "PosAA": 5,
            "PosNA": 13,
            "LengthNA": 3
          },
          {
            "PosAA": 6,
            "PosNA": 16,
            "LengthNA": 3
          },
          {
            "PosAA": 7,
            "PosNA": 19,
            "LengthNA": 3
          },
          {
            "PosAA": 8,
            "PosNA": 22,
            "LengthNA": 3
          },
          {
            "PosAA": 9,
            "PosNA": 25,
            "LengthNA": 3
          },
          {
            "PosAA": 10,
            "PosNA": 28,
            "LengthNA": 3
          },
          {
            "PosAA": 11,
            "PosNA": 31,
            "LengthNA": 3
          },
          {
            "PosAA": 12,
            "PosNA": 34,
            "LengthNA": 3
          },
          {
            "PosAA": 13,
            "PosNA": 37,
            "LengthNA": 3
          },
          {
            "PosAA": 14,
            "PosNA": 40,
            "LengthNA": 3
          },
          {
            "PosAA": 15,
            "PosNA": 43,
            "LengthNA": 3
          },
          {
            "PosAA": 16,
            "PosNA": 46,
            "LengthNA": 3
          },
          {
            "PosAA": 17,
            "PosNA": 49,
            "LengthNA": 3
          },
          {
            "PosAA": 18,
            "PosNA": 52,
            "LengthNA": 3
          },
          {
            "PosAA": 19,
            "PosNA": 55,
            "LengthNA": 3
          },
          {
            "PosAA": 20,
            "PosNA": 58,
            "LengthNA": 3
          },
          {
            "PosAA": 21,
            "PosNA": 61,
            "LengthNA": 3
          },
          {
            "PosAA": 22,
            "PosNA": 64,
            "LengthNA": 3
          },
          {
            "PosAA": 23,
            "PosNA": 67,
            "LengthNA": 3
          },
          {
            "PosAA": 24,
            "PosNA": 70,
            "LengthNA": 3
          },
          {
            "PosAA": 25,
            "PosNA": 73,
            "LengthNA": 3
          },
          {
            "PosAA": 26,
            "PosNA": 76,
            "LengthNA": 3
          },
          {
            "PosAA": 27,
            "PosNA": 79,
            "LengthNA": 3
          },
          {
            "PosAA": 28,
            "PosNA": 82,
            "LengthNA": 3
          },
          {
            "PosAA": 29,
            "PosNA": 85,
            "LengthNA": 3
          },
          {
            "PosAA": 30,
            "PosNA": 88,
            "LengthNA": 3
          },
          {
            "PosAA": 31,
            "PosNA": 91,
            "LengthNA": 3
          },
          {
            "PosAA": 32,
            "PosNA": 94,
            "LengthNA": 3
          },
          {
            "PosAA": 33,
            "PosNA": 97,
            "LengthNA": 3
          },
          {
            "PosAA": 34,
            "PosNA": 100,
            "LengthNA": 3
          },
          {
            "PosAA": 35,
            "PosNA": 103,
            "LengthNA": 3
          },
          {
            "PosAA": 36,
            "PosNA": 106,
            "LengthNA": 3
          },
          {
            "PosAA": 37,
            "PosNA": 109,
            "LengthNA": 3
          },
          {
            "PosAA": 38,
            "PosNA": 112,
            "LengthNA": 3
          },
          {
            "PosAA": 39,
            "PosNA": 115,
            "LengthNA": 3
          },
          {
            "PosAA": 40,
            "PosNA": 118,
            "LengthNA": 3
          },
          {
            "PosAA": 41,
            "PosNA": 121,
            "LengthNA": 3
          },
          {
            "PosAA": 42,
            "PosNA": 124,
            "LengthNA": 3
          },
          {
            "PosAA": 43,
            "PosNA": 127,
            "LengthNA": 3
          },
          {
            "PosAA": 44,
            "PosNA": 130,
            "LengthNA": 3
          },
          {
            "PosAA": 45,
            "PosNA": 133,
            "LengthNA": 3
          },
          {
            "PosAA": 46,
            "PosNA": 136,
            "LengthNA": 3
          },
          {
            "PosAA": 47,
            "PosNA": 139,
            "LengthNA": 3
          },
          {
            "PosAA": 48,
            "PosNA": 142,
            "LengthNA": 3
          },
          {
            "PosAA": 49,
            "PosNA": 145,
            "LengthNA": 3
          },
          {
            "PosAA": 50,
            "PosNA": 148,
            "LengthNA": 3
          },
          {
            "PosAA": 51,
            "PosNA": 151,
            "LengthNA": 3
          },
          {
            "PosAA": 52,
            "PosNA": 154,
            "LengthNA": 3
          },
          {
            "PosAA": 53,
            "PosNA": 157,
            "LengthNA": 3
          },
          {
            "PosAA": 54,
            "PosNA": 160,
            "LengthNA": 3
          },
          {
            "PosAA": 55,
            "PosNA": 163,
            "LengthNA": 3
          },
          {
            "PosAA": 56,
            "PosNA": 166,
            "LengthNA": 3
          },
          {
            "PosAA": 57,
            "PosNA": 169,
            "LengthNA": 3
          },
          {
            "PosAA": 58,
            "PosNA": 172,
            "LengthNA": 3
          },
          {
            "PosAA": 59,
            "PosNA": 175,
            "LengthNA": 3
          },
          {
            "PosAA": 60,
            "PosNA": 178,
            "LengthNA": 3
          },
          {
            "PosAA": 61,
            "PosNA": 181,
            "LengthNA": 3
          },
          {
            "PosAA": 62,
            "PosNA": 184,
            "LengthNA": 3
          },
          {
            "PosAA": 63,
            "PosNA": 187,
            "LengthNA": 3
          },
          {
            "PosAA": 64,
            "PosNA": 190,
            "LengthNA": 3
          },
          {
            "PosAA": 65,
            "PosNA": 193,
            "LengthNA": 3
          },
          {
            "PosAA": 66,
            "PosNA": 196,
            "LengthNA": 3
          },
          {
            "PosAA": 67,
            "PosNA": 199,
            "LengthNA": 3
          },
          {
            "PosAA": 68,
            "PosNA": 202,
            "LengthNA": 3
          },
          {
            "PosAA": 69,
            "PosNA": 205,
            "LengthNA": 3
          },
          {
            "PosAA": 70,
            "PosNA": 208,
            "LengthNA": 3
          },
          {
            "PosAA": 71,
            "PosNA": 211,
            "LengthNA": 3
          },
          {
            "PosAA": 72,
            "PosNA": 214,
            "LengthNA": 3
          },
          {
            "PosAA": 73,
            "PosNA": 217,
            "LengthNA": 3
          },
          {
            "PosAA": 74,
            "PosNA": 220,
            "LengthNA": 3
          },
          {
            "PosAA": 75,
            "PosNA": 223,
            "LengthNA": 3
          },
          {
            "PosAA": 76,
            "PosNA": 226,
            "LengthNA": 3
          },
          {
            "PosAA": 77,
            "PosNA": 229,
            "LengthNA": 3
          },
          {
            "PosAA": 78,
            "PosNA": 232,
            "LengthNA": 3
          },
          {
            "PosAA": 79,
            "PosNA": 235,
            "LengthNA": 3
          },
          {
            "PosAA": 80,
            "PosNA": 238,
            "LengthNA": 3
          },
          {
            "PosAA": 81,
            "PosNA": 241,
            "LengthNA": 3
          },
          {
            "PosAA": 82,
            "PosNA": 244,
            "LengthNA": 3
          },
          {
            "PosAA": 83,
            "PosNA": 247,
            "LengthNA": 3
          },
          {
            "PosAA": 84,
            "PosNA": 250,
            "LengthNA": 3
          },
          {
            "PosAA": 85,
            "PosNA": 253,
            "LengthNA": 3
          },
          {
            "PosAA": 86,
            "PosNA": 256,
            "LengthNA": 3
          },
          {
            "PosAA": 87,
            "PosNA": 259,
            "LengthNA": 3
          },
          {
            "PosAA": 88,
            "PosNA": 262,
            "LengthNA": 3
          },
          {
            "PosAA": 89,
            "PosNA": 265,
            "LengthNA": 3
          },
          {
            "PosAA": 90,
            "PosNA": 268,
            "LengthNA": 3
          },
          {
            "PosAA": 91,
            "PosNA": 271,
            "LengthNA": 3
          },
          {
            "PosAA": 92,
            "PosNA": 274,
            "LengthNA": 3
          },
          {
            "PosAA": 93,
            "PosNA": 277,
            "LengthNA": 3
          },
          {
            "PosAA": 94,
            "PosNA": 280,
            "LengthNA": 3
          },
          {
            "PosAA": 95,
            "PosNA": 283,
            "LengthNA": 3
          },
          {
            "PosAA": 96,
            "PosNA": 286,
            "LengthNA": 3
          },
          {
            "PosAA": 97,
            "PosNA": 289,
            "LengthNA": 3
          },
          {
            "PosAA": 98,
            "PosNA": 292,
            "LengthNA": 3
          },
          {
            "PosAA": 99,
            "PosNA": 295,
            "LengthNA": 3
          },
          {
            "PosAA": 100,
            "PosNA": 298,
            "LengthNA": 3
          },
          {
            "PosAA": 101,
            "PosNA": 301,
            "LengthNA": 3
          },
          {
            "PosAA": 102,
            "PosNA": 304,
            "LengthNA": 3
          },
          {
            "PosAA": 103,
            "PosNA": 307,
            "LengthNA": 3
          },
          {
            "PosAA": 104,
            "PosNA": 310,
            "LengthNA": 3
          },
          {
            "PosAA": 105,
            "PosNA": 313,
            "LengthNA": 3
          },
          {
            "PosAA": 106,
            "PosNA": 316,
            "LengthNA": 3
          },
          {
            "PosAA": 107,
            "PosNA": 319,
            "LengthNA": 3
          },
          {
            "PosAA": 108,
            "PosNA": 322,
            "LengthNA": 3
          },
          {
            "PosAA": 109,
            "PosNA": 325,
            "LengthNA": 3
          },
          {
            "PosAA": 110,
            "PosNA": 328,
            "LengthNA": 3
          },
          {
            "PosAA": 111,
            "PosNA": 331,
            "LengthNA": 3
          },
          {
            "PosAA": 112,
            "PosNA": 334,
            "LengthNA": 3
          },
          {
            "PosAA": 113,
            "PosNA": 337,
            "LengthNA": 3
          },
          {
            "PosAA": 114,
            "PosNA": 340,
            "LengthNA": 3
          },
          {
            "PosAA": 115,
            "PosNA": 343,
            "LengthNA": 3
          },
          {
            "PosAA": 116,
            "PosNA": 346,
            "LengthNA": 3
          },
          {
            "PosAA": 117,
            "PosNA": 349,
            "LengthNA": 3
          },
          {
            "PosAA": 118,
            "PosNA": 352,
            "LengthNA": 3
          },
          {
            "PosAA": 119,
            "PosNA": 355,
            "LengthNA": 3
          },
          {
            "PosAA": 120,
            "PosNA": 358,
            "LengthNA": 3
          },
          {
            "PosAA": 121,
            "PosNA": 361,
            "LengthNA": 3
          },
          {
            "PosAA": 122,
            "PosNA": 364,
            "LengthNA": 3
          },
          {
            "PosAA": 123,
            "PosNA": 367,
            "LengthNA": 3
          },
          {
            "PosAA": 124,
            "PosNA": 370,
            "LengthNA": 3
          },
          {
            "PosAA": 125,
            "PosNA": 373,
            "LengthNA": 3
          },
          {
            "PosAA": 126,
            "PosNA": 376,
            "LengthNA": 3
          },
          {
            "PosAA": 127,
            "PosNA": 379,
            "LengthNA": 3
          },
          {
            "PosAA": 128,
            "PosNA": 382,
            "LengthNA": 3
          },
          {
            "PosAA": 129,
            "PosNA": 385,
            "LengthNA": 3
          },
          {
            "PosAA": 130,
            "PosNA": 388,
            "LengthNA": 3
          },
          {
            "PosAA": 131,
            "PosNA": 391,
            "LengthNA": 3
          },
          {
            "PosAA": 132,
            "PosNA": 394,
            "LengthNA": 3
          },
          {
            "PosAA": 133,
            "PosNA": 397,
            "LengthNA": 3
          },
          {
            "PosAA": 134,
            "PosNA": 400,
            "LengthNA": 3
          },
          {
            "PosAA": 135,
            "PosNA": 403,
            "LengthNA": 3
          },
          {
            "PosAA": 136,
            "PosNA": 406,
            "LengthNA": 3
          },
          {
            "PosAA": 137,
            "PosNA": 409,
            "LengthNA": 3
          },
          {
            "PosAA": 138,
            "PosNA": 412,
            "LengthNA": 3
          },
          {
            "PosAA": 139,
            "PosNA": 415,
            "LengthNA": 3
          },
          {
            "PosAA": 140,
            "PosNA": 418,
            "LengthNA": 3
          },
          {
            "PosAA": 141,
            "PosNA": 421,
            "LengthNA": 3
          },
          {
            "PosAA": 142,
            "PosNA": 424,
            "LengthNA": 3
          },
          {
            "PosAA": 143,
            "PosNA": 427,
            "LengthNA": 3
          },
          {
            "PosAA": 144,
            "PosNA": 430,
            "LengthNA": 3
          },
          {
            "PosAA": 145,
            "PosNA": 433,
            "LengthNA": 3
          },
          {
            "PosAA": 146,
            "PosNA": 436,
            "LengthNA": 3
          },
          {
            "PosAA": 147,
            "PosNA": 439,
            "LengthNA": 3
          },
          {
            "PosAA": 148,
            "PosNA": 442,
            "LengthNA": 3
          },
          {
            "PosAA": 149,
            "PosNA": 445,
            "LengthNA": 3
          },
          {
            "PosAA": 150,
            "PosNA": 448,
            "LengthNA": 3
          },
          {
            "PosAA": 151,
            "PosNA": 451,
            "LengthNA": 3
          },
          {
            "PosAA": 152,
            "PosNA": 454,
            "LengthNA": 3
          },
          {
            "PosAA": 153,
            "PosNA": 457,
            "LengthNA": 3
          },
          {
            "PosAA": 154,
            "PosNA": 460,
            "LengthNA": 3
          },
          {
            "PosAA": 155,
            "PosNA": 463,
            "LengthNA": 3
          },
          {
            "PosAA": 156,
            "PosNA": 466,
            "LengthNA": 3
          },
          {
            "PosAA": 157,
            "PosNA": 469,
            "LengthNA": 3
          },
          {
            "PosAA": 158,
            "PosNA": 472,
            "LengthNA": 3
          },
          {
            "PosAA": 159,
            "PosNA": 475,
            "LengthNA": 3
          },
          {
            "PosAA": 160,
            "PosNA": 478,
            "LengthNA": 3
          },
          {
            "PosAA": 161,
            "PosNA": 481,
            "LengthNA": 3
          },
          {
            "PosAA": 162,
            "PosNA": 484,
            "LengthNA": 3
          },
          {
            "PosAA": 163,
            "PosNA": 487,
            "LengthNA": 3
          },
          {
            "PosAA": 164,
            "PosNA": 490,
            "LengthNA": 3
          },
          {
            "PosAA": 165,
            "PosNA": 493,
            "LengthNA": 3
          },
          {
            "PosAA": 166,
            "PosNA": 496,
            "LengthNA": 3
          },
          {
            "PosAA": 167,
            "PosNA": 499,
            "LengthNA": 3
          },
          {
            "PosAA": 168,
            "PosNA": 502,
            "LengthNA": 3
          },
          {
            "PosAA": 169,
            "PosNA": 505,
            "LengthNA": 3
          },
          {
            "PosAA": 170,
            "PosNA": 508,
            "LengthNA": 3
          },
          {
            "PosAA": 171,
            "PosNA": 511,
            "LengthNA": 3
          },
          {
            "PosAA": 172,
            "PosNA": 514,
            "LengthNA": 3
          },
          {
            "PosAA": 173,
            "PosNA": 517,
            "LengthNA": 3
          },
          {
            "PosAA": 174,
            "PosNA": 520,
            "LengthNA": 3
          },
          {
            "PosAA": 175,
            "PosNA": 523,
            "LengthNA": 3
          },
          {
            "PosAA": 176,
            "PosNA": 526,
            "LengthNA": 3
          },
          {
            "PosAA": 177,
            "PosNA": 529,
            "LengthNA": 3
          },
          {
            "PosAA": 178,
            "PosNA": 532,
            "LengthNA": 3
          },
          {
            "PosAA": 179,
            "PosNA": 535,
            "LengthNA": 3
          },
          {
            "PosAA": 180,
            "PosNA": 538,
            "LengthNA": 3
          },
          {
            "PosAA": 181,
            "PosNA": 541,
            "LengthNA": 3
          },
          {
            "PosAA": 182,
            "PosNA": 544,
            "LengthNA": 3
          },
          {
            "PosAA": 183,
            "PosNA": 547,
            "LengthNA": 3
          },
          {
            "PosAA": 184,
            "PosNA": 550,
            "LengthNA": 3
          },
          {
            "PosAA": 185,
            "PosNA": 553,
            "LengthNA": 3
          },
          {
            "PosAA": 186,
            "PosNA": 556,
            "LengthNA": 3
          },
          {
            "PosAA": 187,
            "PosNA": 559,
            "LengthNA": 3
          },
          {
            "PosAA": 188,
            "PosNA": 562,
            "LengthNA": 3
          },
          {
            "PosAA": 189,
            "PosNA": 565,
            "LengthNA": 3
          },
          {
            "PosAA": 190,
            "PosNA": 568,
            "LengthNA": 3
          },
          {
            "PosAA": 191,
            "PosNA": 571,
            "LengthNA": 3
          },
          {
            "PosAA": 192,
            "PosNA": 574,
            "LengthNA": 3
          },
          {
            "PosAA": 193,
            "PosNA": 577,
            "LengthNA": 3
          },
          {
            "PosAA": 194,
            "PosNA": 580,
            "LengthNA": 3
          },
          {
            "PosAA": 195,
            "PosNA": 583,
            "LengthNA": 3
          },
          {
            "PosAA": 196,
            "PosNA": 586,
            "LengthNA": 3
          },
          {
            "PosAA": 197,
            "PosNA": 589,
            "LengthNA": 3
          },
          {
            "PosAA": 198,
            "PosNA": 592,
            "LengthNA": 3
          },
          {
            "PosAA": 199,
            "PosNA": 595,
            "LengthNA": 3
          },
          {
            "PosAA": 200,
            "PosNA": 598,
            "LengthNA": 3
          },
          {
            "PosAA": 201,
            "PosNA": 601,
            "LengthNA": 3
          },
          {
            "PosAA": 202,
            "PosNA": 604,
            "LengthNA": 3
          },
          {
            "PosAA": 203,
            "PosNA": 607,
            "LengthNA": 3
          },
          {
            "PosAA": 204,
            "PosNA": 610,
            "LengthNA": 3
          },
          {
            "PosAA": 205,
            "PosNA": 613,
            "LengthNA": 3
          },
          {
            "PosAA": 206,
            "PosNA": 616,
            "LengthNA": 3
          },
          {
            "PosAA": 207,
            "PosNA": 619,
            "LengthNA": 3
          },
          {
            "PosAA": 208,
            "PosNA": 622,
            "LengthNA": 3
          },
          {
            "PosAA": 209,
            "PosNA": 625,
            "LengthNA": 3
          },
          {
            "PosAA": 210,
            "PosNA": 628,
            "LengthNA": 3
          },
          {
            "PosAA": 211,
            "PosNA": 631,
            "LengthNA": 3
          },
          {
            "PosAA": 212,
            "PosNA": 634,
            "LengthNA": 3
          },
          {
            "PosAA": 213,
            "PosNA": 637,
            "LengthNA": 3
          },
          {
            "PosAA": 214,
            "PosNA": 640,
            "LengthNA": 3
          },
          {
            "PosAA": 215,
            "PosNA": 643,
            "LengthNA": 3
          },
          {
            "PosAA": 216,
            "PosNA": 646,
            "LengthNA": 3
          },
          {
            "PosAA": 217,
            "PosNA": 649,
            "LengthNA": 3
          },
          {
            "PosAA": 218,
            "PosNA": 652,
            "LengthNA": 3
          },
          {
            "PosAA": 219,
            "PosNA": 655,
            "LengthNA": 3
          },
          {
            "PosAA": 220,
            "PosNA": 658,
            "LengthNA": 3
          },
          {
            "PosAA": 221,
            "PosNA": 661,
            "LengthNA": 3
          },
          {
            "PosAA": 222,
            "PosNA": 664,
            "LengthNA": 3
          },
          {
            "PosAA": 223,
            "PosNA": 667,
            "LengthNA": 3
          },
          {
            "PosAA": 224,
            "PosNA": 670,
            "LengthNA": 3
          },
          {
            "PosAA": 225,
            "PosNA": 673,
            "LengthNA": 3
          },
          {
            "PosAA": 226,
            "PosNA": 676,
            "LengthNA": 3
          },
          {
            "PosAA": 227,
            "PosNA": 679,
            "LengthNA": 3
          },
          {
            "PosAA": 228,
            "PosNA": 682,
            "LengthNA": 3
          },
          {
            "PosAA": 229,
            "PosNA": 685,
            "LengthNA": 3
          },
          {
            "PosAA": 230,
            "PosNA": 688,
            "LengthNA": 3
          },
          {
            "PosAA": 231,
            "PosNA": 691,
            "LengthNA": 3
          },
          {
            "PosAA": 232,
            "PosNA": 694,
            "LengthNA": 3
          },
          {
            "PosAA": 233,
            "PosNA": 697,
            "LengthNA": 3
          },
          {
            "PosAA": 234,
            "PosNA": 700,
            "LengthNA": 3
          },
          {
            "PosAA": 235,
            "PosNA": 703,
            "LengthNA": 3
          },
          {
            "PosAA": 236,
            "PosNA": 706,
            "LengthNA": 3
          },
          {
            "PosAA": 237,
            "PosNA": 709,
            "LengthNA": 3
          },
          {
            "PosAA": 238,
            "PosNA": 712,
            "LengthNA": 3
          },
          {
            "PosAA": 239,
            "PosNA": 715,
            "LengthNA": 3
          },
          {
            "PosAA": 240,
            "PosNA": 718,
            "LengthNA": 3
          },
          {
            "PosAA": 241,
            "PosNA": 721,
            "LengthNA": 3
          },
          {
            "PosAA": 242,
            "PosNA": 724,
            "LengthNA": 3
          },
          {
            "PosAA": 243,
            "PosNA": 727,
            "LengthNA": 3
          },
          {
            "PosAA": 244,
            "PosNA": 730,
            "LengthNA": 3
          },
          {
            "PosAA": 245,
            "PosNA": 733,
            "LengthNA": 3
          },
          {
            "PosAA": 246,
            "PosNA": 736,
            "LengthNA": 3
          },
          {
            "PosAA": 247,
            "PosNA": 739,
            "LengthNA": 3
          },
          {
            "PosAA": 248,
            "PosNA": 742,
            "LengthNA": 3
          },
          {
            "PosAA": 249,
            "PosNA": 745,
            "LengthNA": 3
          },
          {
            "PosAA": 250,
            "PosNA": 748,
            "LengthNA": 3
          },
          {
            "PosAA": 251,
            "PosNA": 751,
            "LengthNA": 3
          },
          {
            "PosAA": 252,
            "PosNA": 754,
            "LengthNA": 3
          },
          {
            "PosAA": 253,
            "PosNA": 757,
            "LengthNA": 3
          },
          {
            "PosAA": 254,
            "PosNA": 760,
            "LengthNA": 3
          },
          {
            "PosAA": 255,
            "PosNA": 763,
            "LengthNA": 3
          },
          {
            "PosAA": 256,
            "PosNA": 766,
            "LengthNA": 3
          },
          {
            "PosAA": 257,
            "PosNA": 769,
            "LengthNA": 3
          },
          {
            "PosAA": 258,
            "PosNA": 772,
            "LengthNA": 3
          },
          {
            "PosAA": 259,
            "PosNA": 775,
            "LengthNA": 3
          },
          {
            "PosAA": 260,
            "PosNA": 778,
            "LengthNA": 3
          },
          {
            "PosAA": 261,
            "PosNA": 781,
            "LengthNA": 3
          },
          {
            "PosAA": 262,
            "PosNA": 784,
            "LengthNA": 3
          },
          {
            "PosAA": 263,
            "PosNA": 787,
            "LengthNA": 3
          },
          {
            "PosAA": 264,
            "PosNA": 790,
            "LengthNA": 3
          },
          {
            "PosAA": 265,
            "PosNA": 793,
            "LengthNA": 3
          },
          {
            "PosAA": 266,
            "PosNA": 796,
            "LengthNA": 3
          },
          {
            "PosAA": 267,
            "PosNA": 799,
            "LengthNA": 3
          },
          {
            "PosAA": 268,
            "PosNA": 802,
            "LengthNA": 3
          },
          {
            "PosAA": 269,
            "PosNA": 805,
            "LengthNA": 3
          },
          {
            "PosAA": 270,
            "PosNA": 808,
            "LengthNA": 3
          },
          {
            "PosAA": 271,
            "PosNA": 811,
            "LengthNA": 3
          },
          {
            "PosAA": 272,
            "PosNA": 814,
            "LengthNA": 3
          },
          {
            "PosAA": 273,
            "PosNA": 817,
            "LengthNA": 3
          },
          {
            "PosAA": 274,
            "PosNA": 820,
            "LengthNA": 3
          },
          {
            "PosAA": 275,
            "PosNA": 823,
            "LengthNA": 3
          },
          {
            "PosAA": 276,
            "PosNA": 826,
            "LengthNA": 3
          },
          {
            "PosAA": 277,
            "PosNA": 829,
            "LengthNA": 3
          },
          {
            "PosAA": 278,
            "PosNA": 832,
            "LengthNA": 3
          },
          {
            "PosAA": 279,
            "PosNA": 835,
            "LengthNA": 3
          },
          {
            "PosAA": 280,
            "PosNA": 838,
            "LengthNA": 3
          },
          {
            "PosAA": 281,
            "PosNA": 841,
            "LengthNA": 3
          },
          {
            "PosAA": 282,
            "PosNA": 844,
            "LengthNA": 3
          },
          {
            "PosAA": 283,
            "PosNA": 847,
            "LengthNA": 3
          },
          {
            "PosAA": 284,
            "PosNA": 850,
            "LengthNA": 3
          },
          {
            "PosAA": 285,
            "PosNA": 853,
            "LengthNA": 3
          },
          {
            "PosAA": 286,
            "PosNA": 856,
            "LengthNA": 3
          },
          {
            "PosAA": 287,
            "PosNA": 859,
            "LengthNA": 3
          },
          {
            "PosAA": 288,
            "PosNA": 862,
            "LengthNA": 3
          },
          {
            "PosAA": 289,
            "PosNA": 865,
            "LengthNA": 3
          },
          {
            "PosAA": 290,
            "PosNA": 868,
            "LengthNA": 3
          },
          {
            "PosAA": 291,
            "PosNA": 871,
            "LengthNA": 3
          },
          {
            "PosAA": 292,
            "PosNA": 874,
            "LengthNA": 3
          },
          {
            "PosAA": 293,
            "PosNA": 877,
            "LengthNA": 3
          },
          {
            "PosAA": 294,
            "PosNA": 880,
            "LengthNA": 3
          },
          {
            "PosAA": 295,
            "PosNA": 883,
            "LengthNA": 3
          },
          {
            "PosAA": 296,
            "PosNA": 886,
            "LengthNA": 3
          },
          {
            "PosAA": 297,
            "PosNA": 889,
            "LengthNA": 3
          },
          {
            "PosAA": 298,
            "PosNA": 892,
            "LengthNA": 3
          },
          {
            "PosAA": 299,
            "PosNA": 895,
            "LengthNA": 3
          },
          {
            "PosAA": 300,
            "PosNA": 898,
            "LengthNA": 3
          },
          {
            "PosAA": 301,
            "PosNA": 901,
            "LengthNA": 3
          },
          {
            "PosAA": 302,
            "PosNA": 904,
            "LengthNA": 3
          },
          {
            "PosAA": 303,
            "PosNA": 907,
            "LengthNA": 3
          },
          {
            "PosAA": 304,
            "PosNA": 910,
            "LengthNA": 3
          },
          {
            "PosAA": 305,
            "PosNA": 913,
            "LengthNA": 3
          },
          {
            "PosAA": 306,
            "PosNA": 916,
            "LengthNA": 3
          },
          {
            "PosAA": 307,
            "PosNA": 919,
            "LengthNA": 3
          },
          {
            "PosAA": 308,
            "PosNA": 922,
            "LengthNA": 3
          },
          {
            "PosAA": 309,
            "PosNA": 925,
            "LengthNA": 3
          },
          {
            "PosAA": 310,
            "PosNA": 928,
            "LengthNA": 3
          },
          {
            "PosAA": 311,
            "PosNA": 931,
            "LengthNA": 3
          },
          {
            "PosAA": 312,
            "PosNA": 934,
            "LengthNA": 3
          },
          {
            "PosAA": 313,
            "PosNA": 937,
            "LengthNA": 3
          },
          {
            "PosAA": 314,
            "PosNA": 940,
            "LengthNA": 3
          },
          {
            "PosAA": 315,
            "PosNA": 943,
            "LengthNA": 3
          },
          {
            "PosAA": 316,
            "PosNA": 946,
            "LengthNA": 3
          },
          {
            "PosAA": 317,
            "PosNA": 949,
            "LengthNA": 3
          },
          {
            "PosAA": 318,
            "PosNA": 952,
            "LengthNA": 3
          },
          {
            "PosAA": 319,
            "PosNA": 955,
            "LengthNA": 3
          },
          {
            "PosAA": 320,
            "PosNA": 958,
            "LengthNA": 3
          },
          {
            "PosAA": 321,
            "PosNA": 961,
            "LengthNA": 3
          },
          {
            "PosAA": 322,
            "PosNA": 964,
            "LengthNA": 3
          },
          {
            "PosAA": 323,
            "PosNA": 967,
            "LengthNA": 3
          },
          {
            "PosAA": 324,
            "PosNA": 970,
            "LengthNA": 3
          },
          {
            "PosAA": 325,
            "PosNA": 973,
            "LengthNA": 3
          },
          {
            "PosAA": 326,
            "PosNA": 976,
            "LengthNA": 3
          },
          {
            "PosAA": 327,
            "PosNA": 979,
            "LengthNA": 3
          },
          {
            "PosAA": 328,
            "PosNA": 982,
            "LengthNA": 3
          },
          {
            "PosAA": 329,
            "PosNA": 985,
            "LengthNA": 3
          },
          {
            "PosAA": 330,
            "PosNA": 988,
            "LengthNA": 3
          },
          {
            "PosAA": 331,
            "PosNA": 991,
            "LengthNA": 3
          },
          {
            "PosAA": 332,
            "PosNA": 994,
            "LengthNA": 3
          },
          {
            "PosAA": 333,
            "PosNA": 997,
            "LengthNA": 3
          },
          {
            "PosAA": 334,
            "PosNA": 1000,
            "LengthNA": 3
          },
          {
            "PosAA": 335,
            "PosNA": 1003,
            "LengthNA": 3
          },
          {
            "PosAA": 336,
            "PosNA": 1006,
            "LengthNA": 3
          },
          {
            "PosAA": 337,
            "PosNA": 1009,
            "LengthNA": 3
          },
          {
            "PosAA": 338,
            "PosNA": 1012,
            "LengthNA": 3
          },
          {
            "PosAA": 339,
            "PosNA": 1015,
            "LengthNA": 3
          },
          {
            "PosAA": 340,
            "PosNA": 1018,
            "LengthNA": 3
          },
          {
            "PosAA": 341,
            "PosNA": 1021,
            "LengthNA": 3
          },
          {
            "PosAA": 342,
            "PosNA": 1024,
            "LengthNA": 3
          },
          {
            "PosAA": 343,
            "PosNA": 1027,
            "LengthNA": 3
          },
          {
            "PosAA": 344,
            "PosNA": 1030,
            "LengthNA": 3
          },
          {
            "PosAA": 345,
            "PosNA": 1033,
            "LengthNA": 3
          },
          {
            "PosAA": 346,
            "PosNA": 1036,
            "LengthNA": 3
          },
          {
            "PosAA": 347,
            "PosNA": 1039,
            "LengthNA": 3
          },
          {
            "PosAA": 348,
            "PosNA": 1042,
            "LengthNA": 3
          },
          {
            "PosAA": 349,
            "PosNA": 1045,
            "LengthNA": 3
          },
          {
            "PosAA": 350,
            "PosNA": 1048,
            "LengthNA": 3
          },
          {
            "PosAA": 351,
            "PosNA": 1051,
            "LengthNA": 3
          },
          {
            "PosAA": 352,
            "PosNA": 1054,
            "LengthNA": 3
          },
          {
            "PosAA": 353,
            "PosNA": 1057,
            "LengthNA": 3
          },
          {
            "PosAA": 354,
            "PosNA": 1060,
            "LengthNA": 3
          },
          {
            "PosAA": 355,
            "PosNA": 1063,
            "LengthNA": 3
          },
          {
            "PosAA": 356,
            "PosNA": 1066,
            "LengthNA": 3
          },
          {
            "PosAA": 357,
            "PosNA": 1069,
            "LengthNA": 3
          },
          {
            "PosAA": 358,
            "PosNA": 1072,
            "LengthNA": 3
          },
          {
            "PosAA": 359,
            "PosNA": 1075,
            "LengthNA": 3
          },
          {
            "PosAA": 360,
            "PosNA": 1078,
            "LengthNA": 3
          },
          {
            "PosAA": 361,
            "PosNA": 1081,
            "LengthNA": 3
          },
          {
            "PosAA": 362,
            "PosNA": 1084,
            "LengthNA": 3
          },
          {
            "PosAA": 363,
            "PosNA": 1087,
            "LengthNA": 3
          },
          {
            "PosAA": 364,
            "PosNA": 1090,
            "LengthNA": 3
          },
          {
            "PosAA": 365,
            "PosNA": 1093,
            "LengthNA": 3
          },
          {
            "PosAA": 366,
            "PosNA": 1096,
            "LengthNA": 3
          },
          {
            "PosAA": 367,
            "PosNA": 1099,
            "LengthNA": 3
          },
          {
            "PosAA": 368,
            "PosNA": 1102,
            "LengthNA": 3
          },
          {
            "PosAA": 369,
            "PosNA": 1105,
            "LengthNA": 3
          },
          {
            "PosAA": 370,
            "PosNA": 1108,
            "LengthNA": 3
          },
          {
            "PosAA": 371,
            "PosNA": 1111,
            "LengthNA": 3
          },
          {
            "PosAA": 372,
            "PosNA": 1114,
            "LengthNA": 3
          },
          {
            "PosAA": 373,
            "PosNA": 1117,
            "LengthNA": 3
          },
          {
            "PosAA": 374,
            "PosNA": 1120,
            "LengthNA": 3
          },
          {
            "PosAA": 375,
            "PosNA": 1123,
            "LengthNA": 3
          },
          {
            "PosAA": 376,
            "PosNA": 1126,
            "LengthNA": 3
          },
          {
            "PosAA": 377,
            "PosNA": 1129,
            "LengthNA": 3
          },
          {
            "PosAA": 378,
            "PosNA": 1132,
            "LengthNA": 3
          },
          {
            "PosAA": 379,
            "PosNA": 1135,
            "LengthNA": 3
          },
          {
            "PosAA": 380,
            "PosNA": 1138,
            "LengthNA": 3
          },
          {
            "PosAA": 381,
            "PosNA": 1141,
            "LengthNA": 3
          },
          {
            "PosAA": 382,
            "PosNA": 1144,
            "LengthNA": 3
          },
          {
            "PosAA": 383,
            "PosNA": 1147,
            "LengthNA": 3
          },
          {
            "PosAA": 384,
            "PosNA": 1150,
            "LengthNA": 3
          },
          {
            "PosAA": 385,
            "PosNA": 1153,
            "LengthNA": 3
          },
          {
            "PosAA": 386,
            "PosNA": 1156,
            "LengthNA": 3
          },
          {
            "PosAA": 387,
            "PosNA": 1159,
            "LengthNA": 3
          },
          {
            "PosAA": 388,
            "PosNA": 1162,
            "LengthNA": 3
          },
          {
            "PosAA": 389,
            "PosNA": 1165,
            "LengthNA": 3
          },
          {
            "PosAA": 390,
            "PosNA": 1168,
            "LengthNA": 3
          },
          {
            "PosAA": 391,
            "PosNA": 1171,
            "LengthNA": 3
          },
          {
            "PosAA": 392,
            "PosNA": 1174,
            "LengthNA": 3
          },
          {
            "PosAA": 393,
            "PosNA": 1177,
            "LengthNA": 3
          },
          {
            "PosAA": 394,
            "PosNA": 1180,
            "LengthNA": 3
          },
          {
            "PosAA": 395,
            "PosNA": 1183,
            "LengthNA": 3
          },
          {
            "PosAA": 396,
            "PosNA": 1186,
            "LengthNA": 3
          },
          {
            "PosAA": 397,
            "PosNA": 1189,
            "LengthNA": 3
          },
          {
            "PosAA": 398,
            "PosNA": 1192,
            "LengthNA": 3
          },
          {
            "PosAA": 399,
            "PosNA": 1195,
            "LengthNA": 3
          },
          {
            "PosAA": 400,
            "PosNA": 1198,
            "LengthNA": 3
          },
          {
            "PosAA": 401,
            "PosNA": 1201,
            "LengthNA": 3
          },
          {
            "PosAA": 402,
            "PosNA": 1204,
            "LengthNA": 3
          },
          {
            "PosAA": 403,
            "PosNA": 1207,
            "LengthNA": 3
          },
          {
            "PosAA": 404,
            "PosNA": 1210,
            "LengthNA": 3
          },
          {
            "PosAA": 405,
            "PosNA": 1213,
            "LengthNA": 3
          },
          {
            "PosAA": 406,
            "PosNA": 1216,
            "LengthNA": 3
          },
          {
            "PosAA": 407,
            "PosNA": 1219,
            "LengthNA": 3
          },
          {
            "PosAA": 408,
            "PosNA": 1222,
            "LengthNA": 3
          },
          {
            "PosAA": 409,
            "PosNA": 1225,
            "LengthNA": 3
          },
          {
            "PosAA": 410,
            "PosNA": 1228,
            "LengthNA": 3
          },
          {
            "PosAA": 411,
            "PosNA": 1231,
            "LengthNA": 3
          },
          {
            "PosAA": 412,
            "PosNA": 1234,
            "LengthNA": 3
          },
          {
            "PosAA": 413,
            "PosNA": 1237,
            "LengthNA": 3
          },
          {
            "PosAA": 414,
            "PosNA": 1240,
            "LengthNA": 3
          },
          {
            "PosAA": 415,
            "PosNA": 1243,
            "LengthNA": 3
          },
          {
            "PosAA": 416,
            "PosNA": 1246,
            "LengthNA": 3
          },
          {
            "PosAA": 417,
            "PosNA": 1249,
            "LengthNA": 3
          },
          {
            "PosAA": 418,
            "PosNA": 1252,
            "LengthNA": 3
          },
          {
            "PosAA": 419,
            "PosNA": 1255,
            "LengthNA": 3
          },
          {
            "PosAA": 420,
            "PosNA": 1258,
            "LengthNA": 3
          },
          {
            "PosAA": 421,
            "PosNA": 1261,
            "LengthNA": 3
          },
          {
            "PosAA": 422,
            "PosNA": 1264,
            "LengthNA": 3
          },
          {
            "PosAA": 423,
            "PosNA": 1267,
            "LengthNA": 3
          },
          {
            "PosAA": 424,
            "PosNA": 1270,
            "LengthNA": 3
          },
          {
            "PosAA": 425,
            "PosNA": 1273,
            "LengthNA": 3
          },
          {
            "PosAA": 426,
            "PosNA": 1276,
            "LengthNA": 3
          },
          {
            "PosAA": 427,
            "PosNA": 1279,
            "LengthNA": 3
          },
          {
            "PosAA": 428,
            "PosNA": 1282,
            "LengthNA": 3
          },
          {
            "PosAA": 429,
            "PosNA": 1285,
            "LengthNA": 3
          },
          {
            "PosAA": 430,
            "PosNA": 1288,
            "LengthNA": 3
          },
          {
            "PosAA": 431,
            "PosNA": 1291,
            "LengthNA": 3
          },
          {
            "PosAA": 432,
            "PosNA": 1294,
            "LengthNA": 3
          },
          {
            "PosAA": 433,
            "PosNA": 1297,
            "LengthNA": 3
          },
          {
            "PosAA": 434,
            "PosNA": 1300,
            "LengthNA": 3
          },
          {
            "PosAA": 435,
            "PosNA": 1303,
            "LengthNA": 3
          },
          {
            "PosAA": 436,
            "PosNA": 1306,
            "LengthNA": 3
          },
          {
            "PosAA": 437,
            "PosNA": 1309,
            "LengthNA": 3
          },
          {
            "PosAA": 438,
            "PosNA": 1312,
            "LengthNA": 3
          },
          {
            "PosAA": 439,
            "PosNA": 1315,
            "LengthNA": 3
          },
          {
            "PosAA": 440,
            "PosNA": 1318,
            "LengthNA": 3
          },
          {
            "PosAA": 441,
            "PosNA": 1321,
            "LengthNA": 3
          },
          {
            "PosAA": 442,
            "PosNA": 1324,
            "LengthNA": 3
          },
          {
            "PosAA": 443,
            "PosNA": 1327,
            "LengthNA": 3
          },
          {
            "PosAA": 444,
            "PosNA": 1330,
            "LengthNA": 3
          },
          {
            "PosAA": 445,
            "PosNA": 1333,
            "LengthNA": 3
          },
          {
            "PosAA": 446,
            "PosNA": 1336,
            "LengthNA": 3
          },
          {
            "PosAA": 447,
            "PosNA": 1339,
            "LengthNA": 3
          },
          {
            "PosAA": 448,
            "PosNA": 1342,
            "LengthNA": 3
          },
          {
            "PosAA": 449,
            "PosNA": 1345,
            "LengthNA": 3
          },
          {
            "PosAA": 450,
            "PosNA": 1348,
            "LengthNA": 3
          },
          {
            "PosAA": 451,
            "PosNA": 1351,
            "LengthNA": 3
          },
          {
            "PosAA": 452,
            "PosNA": 1354,
            "LengthNA": 3
          },
          {
            "PosAA": 453,
            "PosNA": 1357,
            "LengthNA": 3
          },
          {
            "PosAA": 454,
            "PosNA": 1360,
            "LengthNA": 3
          },
          {
            "PosAA": 455,
            "PosNA": 1363,
            "LengthNA": 3
          },
          {
            "PosAA": 456,
            "PosNA": 1366,
            "LengthNA": 3
          },
          {
            "PosAA": 457,
            "PosNA": 1369,
            "LengthNA": 3
          },
          {
            "PosAA": 458,
            "PosNA": 1372,
            "LengthNA": 3
          },
          {
            "PosAA": 459,
            "PosNA": 1375,
            "LengthNA": 3
          },
          {
            "PosAA": 460,
            "PosNA": 1378,
            "LengthNA": 3
          },
          {
            "PosAA": 461,
            "PosNA": 1381,
            "LengthNA": 3
          },
          {
            "PosAA": 462,
            "PosNA": 1384,
            "LengthNA": 3
          },
          {
            "PosAA": 463,
            "PosNA": 1387,
            "LengthNA": 3
          },
          {
            "PosAA": 464,
            "PosNA": 1390,
            "LengthNA": 3
          },
          {
            "PosAA": 465,
            "PosNA": 1393,
            "LengthNA": 3
          },
          {
            "PosAA": 466,
            "PosNA": 1396,
            "LengthNA": 3
          },
          {
            "PosAA": 467,
            "PosNA": 1399,
            "LengthNA": 3
          },
          {
            "PosAA": 468,
            "PosNA": 1402,
            "LengthNA": 3
          },
          {
            "PosAA": 469,
            "PosNA": 1405,
            "LengthNA": 3
          },
          {
            "PosAA": 470,
            "PosNA": 1408,
            "LengthNA": 3
          },
          {
            "PosAA": 471,
            "PosNA": 1411,
            "LengthNA": 3
          },
          {
            "PosAA": 472,
            "PosNA": 1414,
            "LengthNA": 3
          },
          {
            "PosAA": 473,
            "PosNA": 1417,
            "LengthNA": 3
          },
          {
            "PosAA": 474,
            "PosNA": 1420,
            "LengthNA": 3
          },
          {
            "PosAA": 475,
            "PosNA": 1423,
            "LengthNA": 3
          },
          {
            "PosAA": 476,
            "PosNA": 1426,
            "LengthNA": 3
          },
          {
            "PosAA": 477,
            "PosNA": 1429,
            "LengthNA": 3
          },
          {
            "PosAA": 478,
            "PosNA": 1432,
            "LengthNA": 3
          },
          {
            "PosAA": 479,
            "PosNA": 1435,
            "LengthNA": 3
          },
          {
            "PosAA": 480,
            "PosNA": 1438,
            "LengthNA": 3
          },
          {
            "PosAA": 481,
            "PosNA": 1441,
            "LengthNA": 3
          },
          {
            "PosAA": 482,
            "PosNA": 1444,
            "LengthNA": 3
          },
          {
            "PosAA": 483,
            "PosNA": 1447,
            "LengthNA": 3
          },
          {
            "PosAA": 484,
            "PosNA": 1450,
            "LengthNA": 3
          },
          {
            "PosAA": 485,
            "PosNA": 1453,
            "LengthNA": 3
          },
          {
            "PosAA": 486,
            "PosNA": 1456,
            "LengthNA": 3
          },
          {
            "PosAA": 487,
            "PosNA": 1459,
            "LengthNA": 3
          },
          {
            "PosAA": 488,
            "PosNA": 1462,
            "LengthNA": 3
          },
          {
            "PosAA": 489,
            "PosNA": 1465,
            "LengthNA": 3
          },
          {
            "PosAA": 490,
            "PosNA": 1468,
            "LengthNA": 3
          },
          {
            "PosAA": 491,
            "PosNA": 1471,
            "LengthNA": 3
          },
          {
            "PosAA": 492,
            "PosNA": 1474,
            "LengthNA": 3
          },
          {
            "PosAA": 493,
            "PosNA": 1477,
            "LengthNA": 3
          },
          {
            "PosAA": 494,
            "PosNA": 1480,
            "LengthNA": 3
          },
          {
            "PosAA": 495,
            "PosNA": 1483,
            "LengthNA": 3
          },
          {
            "PosAA": 496,
            "PosNA": 1486,
            "LengthNA": 3
          },
          {
            "PosAA": 497,
            "PosNA": 1489,
            "LengthNA": 3
          },
          {
            "PosAA": 498,
            "PosNA": 1492,
            "LengthNA": 3
          },
          {
            "PosAA": 499,
            "PosNA": 1495,
            "LengthNA": 3
          },
          {
            "PosAA": 500,
            "PosNA": 1498,
            "LengthNA": 3
          },
          {
            "PosAA": 501,
            "PosNA": 1501,
            "LengthNA": 3
          },
          {
            "PosAA": 502,
            "PosNA": 1504,
            "LengthNA": 3
          },
          {
            "PosAA": 503,
            "PosNA": 1507,
            "LengthNA": 3
          },
          {
            "PosAA": 504,
            "PosNA": 1510,
            "LengthNA": 3
          },
          {
            "PosAA": 505,
            "PosNA": 1513,
            "LengthNA": 3
          },
          {
            "PosAA": 506,
            "PosNA": 1516,
            "LengthNA": 3
          },
          {
            "PosAA": 507,
            "PosNA": 1519,
            "LengthNA": 3
          },
          {
            "PosAA": 508,
            "PosNA": 1522,
            "LengthNA": 3
          },
          {
            "PosAA": 509,
            "PosNA": 1525,
            "LengthNA": 3
          },
          {
            "PosAA": 510,
            "PosNA": 1528,
            "LengthNA": 3
          },
          {
            "PosAA": 511,
            "PosNA": 1531,
            "LengthNA": 3
          },
          {
            "PosAA": 512,
            "PosNA": 1534,
            "LengthNA": 3
          },
          {
            "PosAA": 513,
            "PosNA": 1537,
            "LengthNA": 3
          },
          {
            "PosAA": 514,
            "PosNA": 1540,
            "LengthNA": 3
          },
          {
            "PosAA": 515,
            "PosNA": 1543,
            "LengthNA": 3
          },
          {
            "PosAA": 516,
            "PosNA": 1546,
            "LengthNA": 3
          },
          {
            "PosAA": 517,
            "PosNA": 1549,
            "LengthNA": 3
          },
          {
            "PosAA": 518,
            "PosNA": 1552,
            "LengthNA": 3
          },
          {
            "PosAA": 519,
            "PosNA": 1555,
            "LengthNA": 3
          },
          {
            "PosAA": 520,
            "PosNA": 1558,
            "LengthNA": 3
          },
          {
            "PosAA": 521,
            "PosNA": 1561,
            "LengthNA": 3
          },
          {
            "PosAA": 522,
            "PosNA": 1564,
            "LengthNA": 3
          },
          {
            "PosAA": 523,
            "PosNA": 1567,
            "LengthNA": 3
          },
          {
            "PosAA": 524,
            "PosNA": 1570,
            "LengthNA": 3
          },
          {
            "PosAA": 525,
            "PosNA": 1573,
            "LengthNA": 3
          },
          {
            "PosAA": 526,
            "PosNA": 1576,
            "LengthNA": 3
          },
          {
            "PosAA": 527,
            "PosNA": 1579,
            "LengthNA": 3
          },
          {
            "PosAA": 528,
            "PosNA": 1582,
            "LengthNA": 3
          },
          {
            "PosAA": 529,
            "PosNA": 1585,
            "LengthNA": 3
          },
          {
            "PosAA": 530,
            "PosNA": 1588,
            "LengthNA": 3
          },
          {
            "PosAA": 531,
            "PosNA": 1591,
            "LengthNA": 3
          },
          {
            "PosAA": 532,
            "PosNA": 1594,
            "LengthNA": 3
          },
          {
            "PosAA": 533,
            "PosNA": 1597,
            "LengthNA": 3
          },
          {
            "PosAA": 534,
            "PosNA": 1600,
            "LengthNA": 3
          },
          {
            "PosAA": 535,
            "PosNA": 1603,
            "LengthNA": 3
          },
          {
            "PosAA": 536,
            "PosNA": 1606,
            "LengthNA": 3
          },
          {
            "PosAA": 537,
            "PosNA": 1609,
            "LengthNA": 3
          },
          {
            "PosAA": 538,
            "PosNA": 1612,
            "LengthNA": 3
          },
          {
            "PosAA": 539,
            "PosNA": 1615,
            "LengthNA": 3
          },
          {
            "PosAA": 540,
            "PosNA": 1618,
            "LengthNA": 3
          },
          {
            "PosAA": 541,
            "PosNA": 1621,
            "LengthNA": 3
          },
          {
            "PosAA": 542,
            "PosNA": 1624,
            "LengthNA": 3
          },
          {
            "PosAA": 543,
            "PosNA": 1627,
            "LengthNA": 3
          },
          {
            "PosAA": 544,
            "PosNA": 1630,
            "LengthNA": 3
          },
          {
            "PosAA": 545,
            "PosNA": 1633,
            "LengthNA": 3
          },
          {
            "PosAA": 546,
            "PosNA": 1636,
            "LengthNA": 3
          },
          {
            "PosAA": 547,
            "PosNA": 1639,
            "LengthNA": 3
          },
          {
            "PosAA": 548,
            "PosNA": 1642,
            "LengthNA": 3
          },
          {
            "PosAA": 549,
            "PosNA": 1645,
            "LengthNA": 3
          },
          {
            "PosAA": 550,
            "PosNA": 1648,
            "LengthNA": 3
          },
          {
            "PosAA": 551,
            "PosNA": 1651,
            "LengthNA": 3
          },
          {
            "PosAA": 552,
            "PosNA": 1654,
            "LengthNA": 3
          },
          {
            "PosAA": 553,
            "PosNA": 1657,
            "LengthNA": 3
          },
          {
            "PosAA": 554,
            "PosNA": 1660,
            "LengthNA": 3
          },
          {
            "PosAA": 555,
            "PosNA": 1663,
            "LengthNA": 3
          },
          {
            "PosAA": 556,
            "PosNA": 1666,
            "LengthNA": 3
          },
          {
            "PosAA": 557,
            "PosNA": 1669,
            "LengthNA": 3
          },
          {
            "PosAA": 558,
            "PosNA": 1672,
            "LengthNA": 3
          },
          {
            "PosAA": 559,
            "PosNA": 1675,
            "LengthNA": 3
          },
          {
            "PosAA": 560,
            "PosNA": 1678,
            "LengthNA": 3
          },
          {
            "PosAA": 561,
            "PosNA": 1681,
            "LengthNA": 3
          },
          {
            "PosAA": 562,
            "PosNA": 1684,
            "LengthNA": 3
          },
          {
            "PosAA": 563,
            "PosNA": 1687,
            "LengthNA": 3
          },
          {
            "PosAA": 564,
            "PosNA": 1690,
            "LengthNA": 3
          },
          {
            "PosAA": 565,
            "PosNA": 1693,
            "LengthNA": 3
          },
          {
            "PosAA": 566,
            "PosNA": 1696,
            "LengthNA": 3
          },
          {
            "PosAA": 567,
            "PosNA": 1699,
            "LengthNA": 3
          },
          {
            "PosAA": 568,
            "PosNA": 1702,
            "LengthNA": 3
          },
          {
            "PosAA": 569,
            "PosNA": 1705,
            "LengthNA": 3
          },
          {
            "PosAA": 570,
            "PosNA": 1708,
            "LengthNA": 3
          },
          {
            "PosAA": 571,
            "PosNA": 1711,
            "LengthNA": 3
          },
          {
            "PosAA": 572,
            "PosNA": 1714,
            "LengthNA": 3
          },
          {
            "PosAA": 573,
            "PosNA": 1717,
            "LengthNA": 3
          },
          {
            "PosAA": 574,
            "PosNA": 1720,
            "LengthNA": 3
          },
          {
            "PosAA": 575,
            "PosNA": 1723,
            "LengthNA": 3
          },
          {
            "PosAA": 576,
            "PosNA": 1726,
            "LengthNA": 3
          },
          {
            "PosAA": 577,
            "PosNA": 1729,
            "LengthNA": 3
          },
          {
            "PosAA": 578,
            "PosNA": 1732,
            "LengthNA": 3
          },
          {
            "PosAA": 579,
            "PosNA": 1735,
            "LengthNA": 3
          },
          {
            "PosAA": 580,
            "PosNA": 1738,
            "LengthNA": 3
          },
          {
            "PosAA": 581,
            "PosNA": 1741,
            "LengthNA": 3
          },
          {
            "PosAA": 582,
            "PosNA": 1744,
            "LengthNA": 3
          },
          {
            "PosAA": 583,
            "PosNA": 1747,
            "LengthNA": 3
          },
          {
            "PosAA": 584,
            "PosNA": 1750,
            "LengthNA": 3
          },
          {
            "PosAA": 585,
            "PosNA": 1753,
            "LengthNA": 3
          },
          {
            "PosAA": 586,
            "PosNA": 1756,
            "LengthNA": 3
          },
          {
            "PosAA": 587,
            "PosNA": 1759,
            "LengthNA": 3
          },
          {
            "PosAA": 588,
            "PosNA": 1762,
            "LengthNA": 3
          },
          {
            "PosAA": 589,
            "PosNA": 1765,
            "LengthNA": 3
          },
          {
            "PosAA": 590,
            "PosNA": 1768,
            "LengthNA": 3
          },
          {
            "PosAA": 591,
            "PosNA": 1771,
            "LengthNA": 3
          },
          {
            "PosAA": 592,
            "PosNA": 1774,
            "LengthNA": 3
          },
          {
            "PosAA": 593,
            "PosNA": 1777,
            "LengthNA": 3
          },
          {
            "PosAA": 594,
            "PosNA": 1780,
            "LengthNA": 3
          },
          {
            "PosAA": 595,
            "PosNA": 1783,
            "LengthNA": 3
          },
          {
            "PosAA": 596,
            "PosNA": 1786,
            "LengthNA": 3
          },
          {
            "PosAA": 597,
            "PosNA": 1789,
            "LengthNA": 3
          },
          {
            "PosAA": 598,
            "PosNA": 1792,
            "LengthNA": 3
          },
          {
            "PosAA": 599,
            "PosNA": 1795,
            "LengthNA": 3
          },
          {
            "PosAA": 600,
            "PosNA": 1798,
            "LengthNA": 3
          },
          {
            "PosAA": 601,
            "PosNA": 1801,
            "LengthNA": 3
          },
          {
            "PosAA": 602,
            "PosNA": 1804,
            "LengthNA": 3
          },
          {
            "PosAA": 603,
            "PosNA": 1807,
            "LengthNA": 3
          },
          {
            "PosAA": 604,
            "PosNA": 1810,
            "LengthNA": 3
          },
          {
            "PosAA": 605,
            "PosNA": 1813,
            "LengthNA": 3
          },
          {
            "PosAA": 606,
            "PosNA": 1816,
            "LengthNA": 3
          },
          {
            "PosAA": 607,
            "PosNA": 1819,
            "LengthNA": 3
          },
          {
            "PosAA": 608,
            "PosNA": 1822,
            "LengthNA": 3
          },
          {
            "PosAA": 609,
            "PosNA": 1825,
            "LengthNA": 3
          },
          {
            "PosAA": 610,
            "PosNA": 1828,
            "LengthNA": 3
          },
          {
            "PosAA": 611,
            "PosNA": 1831,
            "LengthNA": 3
          },
          {
            "PosAA": 612,
            "PosNA": 1834,
            "LengthNA": 3
          },
          {
            "PosAA": 613,
            "PosNA": 1837,
            "LengthNA": 3
          },
          {
            "PosAA": 614,
            "PosNA": 1840,
            "LengthNA": 3
          },
          {
            "PosAA": 615,
            "PosNA": 1843,
            "LengthNA": 3
          },
          {
            "PosAA": 616,
            "PosNA": 1846,
            "LengthNA": 3
          },
          {
            "PosAA": 617,
            "PosNA": 1849,
            "LengthNA": 3
          },
          {
            "PosAA": 618,
            "PosNA": 1852,
            "LengthNA": 3
          },
          {
            "PosAA": 619,
            "PosNA": 1855,
            "LengthNA": 3
          },
          {
            "PosAA": 620,
            "PosNA": 1858,
            "LengthNA": 3
          },
          {
            "PosAA": 621,
            "PosNA": 1861,
            "LengthNA": 3
          },
          {
            "PosAA": 622,
            "PosNA": 1864,
            "LengthNA": 3
          },
          {
            "PosAA": 623,
            "PosNA": 1867,
            "LengthNA": 3
          },
          {
            "PosAA": 624,
            "PosNA": 1870,
            "LengthNA": 3
          },
          {
            "PosAA": 625,
            "PosNA": 1873,
            "LengthNA": 3
          },
          {
            "PosAA": 626,
            "PosNA": 1876,
            "LengthNA": 3
          },
          {
            "PosAA": 627,
            "PosNA": 1879,
            "LengthNA": 3
          },
          {
            "PosAA": 628,
            "PosNA": 1882,
            "LengthNA": 3
          },
          {
            "PosAA": 629,
            "PosNA": 1885,
            "LengthNA": 3
          },
          {
            "PosAA": 630,
            "PosNA": 1888,
            "LengthNA": 3
          },
          {
            "PosAA": 631,
            "PosNA": 1891,
            "LengthNA": 3
          }
        ],
        "AminoAcidsLine": "A  P  I  T  A  Y  A  Q  Q  T  R  G  L  L  G  C  I  I  T  S  L  T  G  R  D  K  N  Q  V  E  G  E  V  Q  I  V  S  T  A  T  Q  T  F  L  A  T  C  I  N  G  V  C  W  T  V  Y  H  G  A  G  T  R  T  I  A  S  P  K  G  P  V  I  Q  M  Y  T  N  V  D  Q  D  L  V  G  W  P  A  P  Q  G  S  R  S  L  T  P  C  T  C  G  S  S  D  L  Y  L  V  T  R  H  A  D  V  I  P  V  R  R  R  G  D  S  R  G  S  L  L  S  P  R  P  I  S  Y  L  K  G  S  S  G  G  P  L  L  C  P  A  G  H  A  V  G  L  F  R  A  A  V  C  T  R  G  V  A  K  A  V  D  F  I  P  V  E  N  L  E  T  T  M  R  S  P  V  F  T  D  N  S  S  P  P  A  V  P  Q  S  F  Q  V  A  H  L  H  A  P  T  G  S  G  K  S  T  K  V  P  A  A  Y  A  A  Q  G  Y  K  V  L  V  L  N  P  S  V  A  A  T  L  G  F  G  A  Y  M  S  K  A  H  G  V  D  P  N  I  R  T  G  V  R  T  I  T  T  G  S  P  I  T  Y  S  T  Y  G  K  F  L  A  D  G  G  C  S  G  G  A  Y  D  I  I  I  C  D  E  C  H  S  T  D  A  T  S  I  L  G  I  G  T  V  L  D  Q  A  E  T  A  G  A  R  L  V  V  L  A  T  A  T  P  P  G  S  V  T  V  S  H  P  N  I  E  E  V  A  L  S  T  T  G  E  I  P  F  Y  G  K  A  I  P  L  E  V  I  K  G  G  R  H  L  I  F  C  H  S  K  K  K  C  D  E  L  A  A  K  L  V  A  L  G  I  N  A  V  A  Y  Y  R  G  L  D  V  S  V  I  P  T  S  G  D  V  V  V  V  S  T  D  A  L  M  T  G  F  T  G  D  F  D  S  V  I  D  C  N  T  C  V  T  Q  T  V  D  F  S  L  D  P  T  F  T  I  E  T  T  T  L  P  Q  D  A  V  S  R  T  Q  R  R  G  R  T  G  R  G  K  P  G  I  Y  R  F  V  A  P  G  E  R  P  S  G  M  F  D  S  S  V  L  C  E  C  Y  D  A  G  C  A  W  Y  E  L  T  P  A  E  T  T  V  R  L  R  A  Y  M  N  T  P  G  L  P  V  C  Q  D  H  L  E  F  W  E  G  V  F  T  G  L  T  H  I  D  A  H  F  L  S  Q  T  K  Q  S  G  E  N  F  P  Y  L  V  A  Y  Q  A  T  V  C  A  R  A  Q  A  P  P  P  S  W  D  Q  M  W  K  C  L  I  R  L  K  P  T  L  H  G  P  T  P  L  L  Y  R  L  G  A  V  Q  N  E  V  T  L  T  H  P  I  T  K  Y  I  M  T  C  M  S  A  D  L  E  V  V  T  ",
        "ControlLine": "::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::...:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::...::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::...:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::",
        "NucleicAcidsLine": "GCGCCCATCACGGCGTACGCCCAGCAGACGAGAGGCCTCCTAGGGTGTATAATCACCAGCCTGACTGGCCGGGACAAAAACCAAGTGGAGGGTGAGGTCCAGATCGTGTCAACTGCTACCCAAACCTTCCTGGCAACGTGCATCAATGGGGTATGCTGGACTGTCTACCACGGGGCCGGAACGAGGACCATCGCATCACCCAAGGGTCCTGTCATCCAGATGTATACCAATGTGGACCAAGACCTTGTGGGCTGGCCCGCTCCTCAAGGTTCCCGCTCATTGACACCCTGCACCTGCGGCTCCTCGGACCTTTACCTGGTCACGAGGCACGCCGATGTCATTCCCGTGCGCCGGCGAGGTGATAGCAGGGGTAGCCTGCTTTCGCCCCGGCCCATTTCCTACTTGAAAGGCTCCTCGGGGGGTCCGCTGTTGTGCCCCGCGGGACACGCCGTGGGCCTATTCAGGGCCGCGGTGTGCACCCGTGGAGTGGCTAAGGCGGTGGACTTTATCCCTGTGGAGAACCTAGAGACAACCATGAGATCCCCGGTGTTCACGGACAACTCCTCTCCACCAGCAGTGCCCCAGAGCTTCCAGGTGGCCCACCTGCAGGCTCCCACCGGCAGCGGTAAGAGCACCAAGGTCCCGGCTGCGTACGCAGCCCAGGGCTACAAGGTGTTGGTGCTCGACCCCTCTGTTGCTGCAACGCTGGGCTTTGGTGCTTACATGTCCAAGGCCCATGGGGTTGATCCTAATATCAGGACCGGGGTGAGAACAATTACCACTGGCAGCCCCATCACGTACTCCACCTACGGCAAGTTCCTTGCCGACGGCGGGTGCTCAGGAGGTGCTTATGACATAATAATTTGTGACGAGTGCCACTCCACGGATGCCACATCCATCTTGGGCATCGGCACTGTCCTTGACCAAGCAGAGACTGCGGGGGCGAGACTGGTTGTGCTCGCCACTGCTACCCCTCCGGGCTCCGTCACTGTGTCCCATCCTAACATCGAGGAGGTTGCTCTGTCCACCACCGGAGAGATCCCTTTTTACGGCAAGGCTATCCCCCTCGAGGTGATCAAGGGGGGAAGACATCTCATCTTCTGCCACTCAAAGAAGAAGTGCGACGAGCTCGCCGCGAAGCTGGCCGCATTGGGCATCAATGCCGTGGCCTACTACCGCGGTCTTGACGTGTCTGTCATCCCGACCAGCGGCGATGTTGTCGTCGTGTCGACCGATGCTCTCATGACTGGCTTTACCGGCGACTTCGACTCTGTGATAGACTGCAACACGTGTGTCACTCAGACAGTCGATTTCAGCCTTGACCCTACCTTTACCATTGAGACAACCACGCTCCCCCAGGATGCTGTCTCCAGGACTCAACGCCGGGGCAGGACTGGCAGGGGGAAGCCAGGCATCTACAGATTTGTGGCACCGGGGGAGCGCCCCTCCGGCATGTTCGACTCGTCCGTCCTCTGTGAGTGCTATGACGCGGGCTGTGCTTGGTATGAGCTCACGCCCGCCGAGACTACAGTTAGGCTACGAGCGTACATGAACACCCCGGGGCTTCCCGTGTGCCAGGACCATCTTGAATTTTGGGAGGGCGTCTTTACGGGCCTCACTCATATAGATGCCCACTTTCTATCCCAGACAAAGCAGAGTGGGGAGAACTTTCCTTACCTGGTAGCGTACCAAGCCACCGTGTGCGCTAGGGCTCAAGCCCCTCCCCCATCGTGGGACCAGATGTGGAAGTGTTTGATCCGCCTTAAACCCACCCTCCATGGGCCAACACCCCTGCTATACAGACTGGGCGCTGTTCAGAATGAAGTCACCCTGACGCACCCAATCACCAAATACATCATGACATGCATGTCGGCCGACCTGGAGGTCGTCACG",
        "IsSimpleAlignment": true
      },
      "Error": "",
      "Err": null
    }
  ]
}''')  # noqa


class TestIntegrated(unittest.TestCase):

    def test_align(self):
        pynucamino.Nucamino.cache_clear()
        aligned = pynucamino.align(TEST_FASTA, "hcv1a", genes=("NS3",))
        self.assertEqual(aligned, EXPECTED_OUTPUT)
