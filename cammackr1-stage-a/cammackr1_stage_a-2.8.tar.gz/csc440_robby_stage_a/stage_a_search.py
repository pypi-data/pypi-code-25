class Search:
    search_area = []
    matches = []

    def __init__(self, term, search_area):
        self.search_area = search_area
        self.matches = []

    def clear(self):
        self.matches = []

    def simple_search(self, term):  # Search through the the search area using the value of term.
        for item in self.search_area:
            if item == term:
                self.matches.append(item)

    def attr_search(self, term, attr):  # Search for a specific attribute within the objects in the search area.
        for item in self.search_area:
            if getattr(item, attr) == term:
                self.matches.append(item)

    def range_search(self, low_term, high_term, inclusive=False):  # Search within a specific range
        if inclusive:
            for item in self.search_area:
                if low_term <= item <= high_term:
                    self.matches.append(item)
        else:
            for item in self.search_area:
                if low_term < item < high_term:
                    self.matches.append(item)


class Tester:
    tots = 0
    title = ""

    def __init__(self, tots, title):
        self.tots = tots
        self.title = title


