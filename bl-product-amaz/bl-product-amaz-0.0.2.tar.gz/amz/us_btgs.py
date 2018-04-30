from amz.database import DataBase

class US_btgs(DataBase):
    def __int__(self):
        super(US_btgs, self).__init__()
        #self.us_btg = self.db.us_btgs

    def get_btg_dataset(self, offset=0, limit=100):
        query = {}

        try:
            r = self.db.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        return list(r)

    def get_btg_by_node_id(self, node_id, offset=0, limit=10):
        query = {}
        query['node_id'] = node_id

        try:
            r = self.db.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)

        return list(r)

    def get_btg_by_classification(self, classification, offset=0, limit=10):
        query = {}
        query['classification'] = classification

        try:
            r = self.db.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)
        return list(r)

    def get_btg_by_classification_field(self, classification_field, offset=0, limit=10):
        query = {}
        query['classification_field'] = classification_field

        try:
            r = self.db.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)
        return list(r)

    def get_btg_by_valid_value(self, valid_value, offset=0, limit=10):
        query = {}
        query['valid_value'] = valid_value

        try:
            r = self.db.us_btgs.find(query).skip(offset).limit(limit)
        except Exception as e:
            print(e)
        return list(r)

