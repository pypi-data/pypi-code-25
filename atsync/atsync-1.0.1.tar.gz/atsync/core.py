import airtable
import time

from collections import defaultdict


AIRTABLE_SPEED_LIMIT = .2

class RelatedTable:
    def __init__(self, base_key, api_key, table_name, primary_key, related_on):
        self.primary_key = primary_key
        self.related_on = related_on

        self.airtable = airtable.Airtable(
                base_key,
                table_name,
                api_key)
        self.records = self.airtable.get_all()
        self.hashtable = {}
        for record in self.records:
            fields = defaultdict(lambda: "invalid", record['fields'])
            self.hashtable.update(
                    {fields[self.primary_key]: record['id']})
        time.sleep(AIRTABLE_SPEED_LIMIT)

    def get_id(self, search_key):
        try:
            record_id = self.hashtable[search_key]
        except KeyError:
            new_record = self.airtable.insert(
                    {self.primary_key: search_key})
            time.sleep(AIRTABLE_SPEED_LIMIT)
            self.hashtable.update(
                    {new_record['fields'][self.primary_key]: new_record['id']})
            record_id = self.hashtable[search_key]

        return record_id


class Table:
    def __init__(self, primary_key, base_key,
                 table_name, api_key, related_tables):
        self.primary_key = primary_key
        self.airtable = airtable.Airtable(base_key,
                                          table_name,
                                          api_key)
        self.records = self.airtable.get_all()
        time.sleep(AIRTABLE_SPEED_LIMIT)
        self.related_tables = [RelatedTable(base_key=base_key,
                                            api_key=api_key,
                                            **related_table)
                               for related_table in related_tables]

    def update_record(self, record):

        # new *copy* of record with foreign key fields updated
        new_record = self.clean_record(self.convert_related(record))
        # get current record
        current_record = self.get_record(record[self.primary_key])
        # if the same as local copy, ignore
        # if different to local copy, update
        if new_record != current_record['fields']:
            self.airtable.update(current_record['id'], new_record)
            time.sleep(AIRTABLE_SPEED_LIMIT)

    def get_record(self, search_key):
        for record in self.records:
            if record['fields'][self.primary_key] == search_key:
                return record

        new_record = self.airtable.insert({self.primary_key: search_key})
        time.sleep(AIRTABLE_SPEED_LIMIT)
        self.records.append(new_record)

        return new_record

    def convert_related(self, record):
        new_record = dict(record)
        if self.related_tables:
            for related_table in self.related_tables:
                if record[related_table.related_on]:
                    new_record[related_table.related_on] = [
                               related_table.get_id(
                                   record[related_table.related_on]),
                              ]

        return new_record

    @staticmethod
    def clean_record(record):
        return {k: v for k, v in record.items() if v}
