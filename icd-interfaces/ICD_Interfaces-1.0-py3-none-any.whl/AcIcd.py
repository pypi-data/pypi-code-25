from models import interfaces
from typing import List, Dict, Any


class AcIcd:

    def __init__(self, name: str) -> None:
        self.attributes: Dict[str, str] = {}
        self.items: List[Any] = []
        self.name = name
        self.Author = ''
        self.Application_Name = ''
        self.Last_Modification_Date = ''
        self.Company_Name = ''

    def add_item(self, item: object) -> None:
        if isinstance(item, interfaces.Interface):
            self.items.append(item)

    def sort_items(self) -> None:
        self.items = sorted(self.items, key=lambda x: x.name, reverse=False)

    def sort_item_attributes(self, order_dict: Dict[str, List[str]]) -> None:
        for item in self.items:
            item.sort_attributes(order_dict[item.name])

    def get_items_by_type(self, item_type: str) -> List[str]:
        list = []
        for item in self.items:
            if item.name == item_type:
                list.append(item)
        return list

    def to_dict(self) -> Dict[str, Any]:
        data = vars(self)
        for key in range(len(data['items'])):
            data['items'][key] = data['items'][key].to_dict()

        return data
