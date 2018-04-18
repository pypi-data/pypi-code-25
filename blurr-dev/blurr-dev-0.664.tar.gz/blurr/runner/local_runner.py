"""
Usage:
    local_runner.py --raw-data=<files> --streaming-dtc=<file> [--window-dtc=<file>] [--output-file=<file>]
    local_runner.py (-h | --help)
"""
import csv
import json
from typing import List, Optional, Any

from collections import defaultdict

from blurr.core.record import Record
from blurr.core.syntax.schema_validator import validate
from blurr.runner.data_processor import DataProcessor, SimpleJsonDataProcessor
from blurr.runner.runner import Runner


class LocalRunner(Runner):
    def __init__(self,
                 local_json_files: List[str],
                 stream_dtc_file: str,
                 window_dtc_file: Optional[str] = None,
                 data_processor: DataProcessor = SimpleJsonDataProcessor()):
        super().__init__(local_json_files, stream_dtc_file, window_dtc_file, data_processor)

        self._identity_records = defaultdict(list)
        self._block_data = {}
        self._window_data = defaultdict(list)

    def _validate_dtc_syntax(self) -> None:
        validate(self._stream_dtc)
        if self._window_dtc is not None:
            validate(self._window_dtc)

    def _consume_file(self, file: str) -> None:
        with open(file) as f:
            for data_str in f:
                for identity, time_record in self.get_per_identity_records(data_str):
                    self._identity_records[identity].append(time_record)

    def execute_for_all_identities(self) -> None:
        for identity_records in self._identity_records.items():
            data = self.execute_per_identity_records(identity_records)
            if self._window_dtc:
                self._window_data.update(data)
            else:
                self._block_data.update(data)

    def execute(self) -> Any:
        for file in self._raw_files:
            self._consume_file(file)

        self.execute_for_all_identities()
        return self._window_data if self._window_dtc else self._block_data

    def print_output(self, data) -> None:
        for row in data.items():
            print(json.dumps(row, default=str))

    def write_output_file(self, output_file: str, data):
        if not self._window_dtc:
            with open(output_file, 'w') as file:
                for row in data.items():
                    file.write(json.dumps(row, default=str))
                    file.write('\n')
        else:
            header = []
            for data_rows in data.values():
                for data_row in data_rows:
                    header = list(data_row.keys())
                    break
            header.sort()
            with open(output_file, 'w') as csv_file:
                writer = csv.DictWriter(csv_file, header)
                writer.writeheader()
                for data_rows in data.values():
                    writer.writerows(data_rows)
