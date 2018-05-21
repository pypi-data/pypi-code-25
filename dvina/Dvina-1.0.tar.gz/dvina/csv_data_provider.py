import csv


class CsvDataProvider:
    """Provides functionality to use csv file as a data source for the library.
    The constructor returns an iterable object over examples which allows going over the file multiple times.
    Every example is a dictionary with the keys taken from the header and the string values
    taken from the corresponding line in the file. If the header is not present, keys will be named
    `id, Attribute 0, Attribute 1, ...`"""
    def __init__(self, csv_file_name, has_header=True, **kwargs):
        """
        Parameters
        ----------
        csv_file_name : string
            location of the csv file
        has_header : bool
            whether the file has a header
        kwargs : dict
            dictionary of arguments to be fed into Python `csv.reader`
        """
        self.kwargs = kwargs
        self.csv_file_name = csv_file_name
        self.has_header = has_header
        with open(csv_file_name, 'r') as f:
            reader = csv.reader(f, kwargs)
            self.header = next(reader)
            if not self.has_header:
                # if there is no header, we assume the first column is ID, and the next ones are attributes
                self.header = ["id"] + (["Attribute {0}".format(i) for i in range(len(self.header)-1)])

    def __iter__(self):
        """
        Reads a csv file line by line and returns dictionary objects with attributes
        Yields
        -------
            an iterator over the examples
        """
        with open(self.csv_file_name, 'r') as csv_file:
            file_reader = csv.reader(csv_file, self.kwargs)
            if self.has_header:
                next(file_reader)
            for line in file_reader:
                example = {}
                for ci in range(len(self.header)):
                    example[self.header[ci]] = line[ci]
                yield example
