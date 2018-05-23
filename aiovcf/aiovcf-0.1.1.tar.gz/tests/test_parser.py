import related

from aiovcf.models import (
    Field,
    FieldIndex,
    Genotype,
    Meta,
    Record,
    SampleRecord,
    SamplesIndex,
    Value,
)
from aiovcf.parser import Parser


def test_format_field():
    assert Parser.parse(
        '##FORMAT=<ID=GQ,Number=1,Type=Integer,Description="Genotype Quality">'
    ) == Field(
        section="FORMAT",
        id="GQ",
        number="1",
        type="Integer",
        description="Genotype Quality",
    )


def test_info_field():
    assert Parser.parse(
        '##INFO=<ID=AF,Number=A,Type=Float,Description="Allele Frequency">'
    ) == Field(
        section="INFO",
        id="AF",
        number="A",
        type="Float",
        description="Allele Frequency",
    )


def test_contig_ignored():
    actual = Parser.parse(
        "##contig=<ID=20,length=62435964,assembly=B36,"
        'md5=f126cdf8a6e0c7f379d618ff66beb2da,species="Homo sapiens",'
        "taxonomy=x> "
    )

    expected = Field(
        section="contig",
        id="20",
        number=None,
        type=None,
        description=None,
        other=[
            Value(name="length", value=62435964),
            Value(name="assembly", value="B36"),
            Value(name="md5", value="f126cdf8a6e0c7f379d618ff66beb2da"),
            Value(name="species", value="Homo sapiens"),
            Value(name="taxonomy", value="x"),
        ],
    )

    assert related.to_json(expected) == related.to_json(actual)


def test_meta():
    assert Parser.parse("##fileformat=VCFv4.1") == Meta(
        name="fileformat", value="VCFv4.1"
    )


def test_samples():
    assert Parser.parse(
        "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	"
        "NA00001	NA00002	NA00003"
    ) == SamplesIndex(samples=["NA00001", "NA00002", "NA00003"])


def test_record():
    field_index = FieldIndex()
    field_index.sample.add(
        Parser.parse(
            '##FORMAT=<ID=AO,Number=A,Type=Integer,Description="Alternate '
            'allele observation count"> '
        )
    )

    samples_index = Parser.parse(
        "#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	NA00001"
        "	NA00002	NA00003"
    )

    actual = Parser.parse(
        "21	4242421	.	T	A	30	.	.	GT:AO	0|0:0.1	0|1:0.2	0/0:0.3",
        field_index=field_index,
        samples_index=samples_index,
    )

    # . means not None, not just []
    assert actual.filters is None

    expected = Record(
        chromosome="21",
        position=4242421,
        id=None,
        ref="T",
        alts=["A"],
        quality=30,
        filters=None,
        info={},
        format=["GT", "AO"],
        samples=[
            SampleRecord(
                sample_id="NA00001",
                genotype=Genotype(value="0|0", alleles={0}, is_phased=True),
                info={"AO": Value(name="AO", value=0.1)},
            ),
            SampleRecord(
                sample_id="NA00002",
                genotype=Genotype(value="0|1", alleles={0, 1}, is_phased=True),
                info={"AO": Value(name="AO", value=0.2)},
            ),
            SampleRecord(
                sample_id="NA00003",
                genotype=Genotype(value="0/0", alleles={0}, is_phased=False),
                info={"AO": Value(name="AO", value=0.3)},
            ),
        ],
    )

    # related default is overriding None
    expected.filters = None

    expect = related.to_json(expected)
    actual = related.to_json(actual)

    assert expect == actual, f"Mismatch:\n\n{expect}\n\n{actual}"
