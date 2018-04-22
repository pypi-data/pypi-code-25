#! /usr/bin/env py.test
# -*- coding: utf-8 -*-

import pytest
from GangaCK.Jobtree.Index import Index

#===============================================================================
# JT INDEX
#===============================================================================

@pytest.mark.parametrize('arg, output', (
  ([]         , u''),
  ([1]        , u'├--'),
  ([4]        , u'├--'),
  ([-4]       , u'├--'),
  ([ 4, 1]    , u'|  ├--'),
  ([-4, 1]    , u'   ├--'),
  ([-4, 1, 1] , u'   |  ├--'),
  ([-4, 1,-2] , u'   |  ├--'),
  ([-4,-2]    , u'   ├--'),
  ([-4,-2,-1] , u'      ├--'),
))
def test_index_indent(arg, output):
  assert Index(arg).indent() == output.encode('utf-8')

@pytest.mark.parametrize('arg, output', (
  ([]         , u''),
  ([-4,1, 1  ], u'   |  |  '),
  ([-4,1,-2  ], u'   |     '),
  ([-4,1,-2,1], u'   |     |  '),
))
def test_index_indent_nodash(arg, output):
  assert Index(arg).indent(with_dash=False) == output.encode('utf-8')
