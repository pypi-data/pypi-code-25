

class MembershipFilter:
    def __init__(self, identifier):
        """The MembershipFilter class allows you define a universe context based on the membership of a parent entity

        To create an MembershipFilter, specify the identifier of the parent entity.

        MembershipFilter('STOXX60')
            -->> creates a filter where entities are members of STOXX 60

        Args:
            identifier: identifier of the parent entiry
        """
        self._identifier = identifier
