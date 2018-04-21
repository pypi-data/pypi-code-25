import pytest

from termsquery import TermsQuery, SyntaxError


def test_parsing():
    src = 'a & ((b | c) & ~d) & x'
    TermsQuery(src)


def test_parsing_error():
    src = 'a & b;'
    with pytest.raises(SyntaxError):
        TermsQuery(src)
    src = 'a & (b | c'
    with pytest.raises(SyntaxError):
        TermsQuery(src)
    src = 'a && (b | c)'
    with pytest.raises(SyntaxError):
        TermsQuery(src)
    src = 'a & b ~| c'
    with pytest.raises(SyntaxError):
        TermsQuery(src)


def test_query_operators_priority():
    src = 'A | B | C & D'  # == A | B | (C & D)
    query = TermsQuery(src)
    assert False == query({'C'})
    assert True == query({'A'})
    assert True == query({'C', 'D'})


def test_query_not_expr():
    src = 'A | ~(B & D)'
    query = TermsQuery(src)
    assert True == query({'A'})
    assert False == query({'B', 'D'})
    assert True == query({'D'})


def test_query_with_quoted_term():
    container = {'item A', 'item B', 'item C'}
    query = TermsQuery('"item B" | C ')
    assert True == query(container)


def test_query_exec_with_terms_conversion():
    src = 'A | B'
    query = TermsQuery(src)
    assert False == query({'a'})
    query.convert_values(lambda v: v.lower())
    assert True == query({'a'})


def test_pickling_unpickling():
    import pickle

    src = 'A | ~(B & D)'

    query_orig = TermsQuery(src)
    query_dump = pickle.dumps(query_orig)
    query_unpickled = pickle.loads(query_dump)

    assert {t.value for t in query_orig.terms} == {t.value for t in query_unpickled.terms}
    for query in (query_orig, query_unpickled):
        assert True == query({'A'})
        assert False == query({'B', 'D'})
        assert True == query({'D'})


if __name__ == '__main__':
    pytest.main()
