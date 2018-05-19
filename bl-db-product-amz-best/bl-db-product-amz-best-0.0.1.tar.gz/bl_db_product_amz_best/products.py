from bl_db_product_amz_best.database import DataBase

class Products(DataBase):
  def __init__(self):
    super(Products, self).__init__()
    self.products = self.db.products

  def get_products_by_node_id(self, node_id, offset=0, limit=100):
      query = {}

      if node_id is not None:
          query['node_id'] = node_id

      try:
          r = self.db.products.find(query).skip(offset).limit(limit)
      except Exception as e:
          print(e)

      return list(r)
