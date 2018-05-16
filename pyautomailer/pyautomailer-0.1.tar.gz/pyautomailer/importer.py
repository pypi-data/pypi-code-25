class Importer:

    records_fields = [] # List of input file fields, first is always email to.
    file_readed = False # Indicates that file is readed successfully or not.

    def __init__(self, input_file):
        self.input_file = input_file
        self.read_file()

    def read_file(self):
        try:
            with open(self.input_file) as f:
                for line in f:
                    record = []
                    for field in line.rstrip().split(';'):
                        record.append(field)
                    self.records_fields.append(record)
            f.close()
            self.file_readed = True
        except FileNotFoundError:
            print('Source file not found!')
