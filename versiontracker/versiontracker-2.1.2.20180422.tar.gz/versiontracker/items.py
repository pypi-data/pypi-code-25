from scrapy import Field, Item as _BaseItem


class Item(_BaseItem):
    date = Field()
    id = Field()
    response = Field()
    url = Field()
    version = Field()
