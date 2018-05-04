import excel_to_json.columntitle as columntitle


class Sheet:
    def __init__(self, title):
        self.title = title
        self.datas = []
        self.anchors = {}
        self.joins = {}

    def parse(self, sheet):
        for column in filter(lambda col: len(col) > 1 and columntitle.is_valid(col[0].value), sheet.columns):
            title = column[0].value.strip()
            decorator = columntitle.parse_decorator(title)
            for row_index in range(1, len(column)):
                if decorator is columntitle.Decorator.Empty:
                    self.parse_data(row_index - 1, title, column[row_index].value)
                elif decorator is columntitle.Decorator.Anchor:
                    self.parse_anchor(row_index - 1, title, column[row_index].value)
                elif decorator is columntitle.Decorator.Join:
                    self.parse_join(row_index - 1, title, column[row_index].value)

    def lazy_get_data(self, row_index):
        while len(self.datas) <= row_index:
            self.datas.append({})
        return self.datas[row_index]

    def parse_data(self, row_index, title, val):
        if val is not None and str(val).strip() != '':
            component_container = self.lazy_get_data(row_index)
            components = columntitle.parse_components(title)
            for type, name in components:
                if type is columntitle.Type.Object:
                    if name not in component_container:
                        component_container[name] = {}
                    component_container = component_container[name]
                elif type is columntitle.Type.Array:
                    component_container[name] = str(val).split(',')
                elif type is columntitle.Type.Attri:
                    component_container[name] = val

    def parse_join(self, row_index, title, val):
        if val is not None and str(val).strip() != '':
            pure_title = columntitle.title_without_decorator(title)
            row_data = self.lazy_get_data(row_index)
            if pure_title not in self.joins:
                self.joins[pure_title] = {}
            if val not in self.joins[pure_title]:
                self.joins[pure_title][val] = []
            self.joins[pure_title][val].append(row_data)

    def parse_anchor(self, row_index, title, val):
        if val is not None and str(val).strip() != '':
            # strip decorator
            pure_title = columntitle.title_without_decorator(title)
            anchor_setter = None
            component_container = self.lazy_get_data(row_index)
            components = columntitle.parse_components(pure_title)
            for type, name in components:
                if type is columntitle.Type.Object:
                    if name not in component_container:
                        component_container[name] = {}
                    component_container = component_container[name]
                elif type is columntitle.Type.Array:
                    component_container[name] = []

                    def setter(data):
                        component_container[name].append(data)
                    anchor_setter = setter
                elif type is columntitle.Type.Attri:
                    def setter(data):
                        component_container[name] = data
                    anchor_setter = setter
            if pure_title not in self.anchors:
                self.anchors[pure_title] = {}
            self.anchors[pure_title][val] = anchor_setter

    def get_anchor_setter(self, title, val):
        # strip decorator
        pure_title = columntitle.title_without_decorator(title)
        setter = None
        if pure_title in self.anchors:
            title_dict = self.anchors[pure_title]
            if val in title_dict:
                setter = title_dict[val]
        return setter

    def get_join(self, join_target, identify):
        return self.joins[columntitle.title_without_decorator(join_target)][identify]
