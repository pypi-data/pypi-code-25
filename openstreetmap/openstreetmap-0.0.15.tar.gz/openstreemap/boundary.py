"""
-------------------------------------------------
   Author :       galen
   date：          2018/5/21
-------------------------------------------------
   Description:
-------------------------------------------------
"""


class Boundary:
    def __init__(self):
        self.name = ''
        self.relation_id = ''
        self.boundary_outer = ''
        self.boundary_inner = ''

    @property
    def info(self):
        data = {
            'name': self.name,
            "relation_id": self.relation_id,
            'boundary': {
                'outer': self.boundary_outer,
                'inner': self.boundary_inner
            }
        }
        return data
