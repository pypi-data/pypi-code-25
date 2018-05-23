from aiovcf.models import Record


def test_add_filter():
    record = Record()
    assert record.filters == []

    record.add_filter(None)
    assert record.filters is None

    record.add_filter("PASS")
    assert record.filters == []

    record.add_filter("j123")
    assert record.filters == ["j123"]

    record.add_filter("k456")
    assert record.filters == ["j123", "k456"]

    record.add_filter("PASS")
    assert record.filters == ["j123", "k456"]

    record.add_filter(None)
    assert record.filters == ["j123", "k456"]
