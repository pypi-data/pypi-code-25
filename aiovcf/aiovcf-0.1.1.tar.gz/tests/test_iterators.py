# from aiovcf import reader
import os

import pytest
import related

from aiovcf import iter_file, iter_calls

INPUT_VCF = os.path.join(os.path.dirname(__file__), "input_vcf")
OUTPUT_RECS = os.path.join(os.path.dirname(__file__), "output_recs")
OUTPUT_CALLS = os.path.join(os.path.dirname(__file__), "output_calls")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_vcf",
    [
        os.path.join(INPUT_VCF, fname)
        for fname in sorted(os.listdir(INPUT_VCF))
    ],
)
async def test_iter_file(input_vcf):
    assert os.path.isfile(input_vcf)
    filename = os.path.basename(input_vcf)[:-4]

    # check records

    output_recs = os.path.join(OUTPUT_RECS, f"{filename}.json")
    assert os.path.isfile(output_recs), f"Output recs is missing: {filename}"

    all_records = []
    async for records in iter_file(input_vcf):
        all_records.append(records)

    actual = related.to_json(all_records, suppress_empty_values=True)
    expect = open(output_recs).read().strip()
    assert expect == actual, f"{filename} Mismatch:\n{actual}\n"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "input_vcf",
    [
        os.path.join(INPUT_VCF, fname)
        for fname in sorted(os.listdir(INPUT_VCF))
    ],
)
async def test_iter_calls(input_vcf):
    assert os.path.isfile(input_vcf)
    filename = os.path.basename(input_vcf)[:-4]

    # check calls

    output_calls = os.path.join(OUTPUT_CALLS, f"{filename}.json")
    assert os.path.isfile(output_calls), f"Output calls is missing: {filename}"

    all_calls = []
    async for call in iter_calls(input_vcf):
        all_calls.append(call)

    actual = related.to_json(all_calls, suppress_empty_values=True)
    expect = open(output_calls).read().strip()
    assert expect == actual, f"{filename} Mismatch:\n\n{actual}"
