class Search:
    search_area = []
    matches = []

    def __init__(self, search_area):
        self.search_area = search_area
        self.matches = []

    def clear(self):
        self.matches = []

    def simple_search(self, term,):  # Search through the the search area using the value of term.
        for item in self.search_area:
            if item == term:
                self.matches.append(item)

    def attr_search(self, term, attr):  # Search for a specific attribute within the objects in the search area.
        for item in self.search_area:
            if getattr(item, attr) == term:
                self.matches.append(item)

