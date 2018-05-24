from apache_beam import PTransform


# Performs one transform... then passes the collection through to another.
class Reemitter(PTransform):

  def __init__(self, transform):

    self.transform = transform

  def expand(self, collection):
    collection | self.transform
    return collection
