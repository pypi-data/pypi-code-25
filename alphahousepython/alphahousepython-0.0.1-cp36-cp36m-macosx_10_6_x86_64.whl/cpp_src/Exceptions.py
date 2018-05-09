


class IncorrectHaplotypeNumberError(Exception):
    """Exception thrown when there is an incorrect number of haplotypes given (2 is usually expected)"""
    def __init__(self):
        Exception.__init__(self, "Incorrect number of haplotypes present")


class NoGenotypeException(Exception):
    """Exception to be thrown when there is no genotype information available"""

    def __init__(self):
        Exception.__init__(self, "No Genotype Information Present")


class NoPointerException(Exception):

    def __init__(self):
        Exception.__init__(self, "No Pointer Present!")
