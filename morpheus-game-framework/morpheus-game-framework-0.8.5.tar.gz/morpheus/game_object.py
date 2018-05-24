class GameObject:
    def json(self, hidden=False):
        return self._parse_dict(self.__dict__, hidden)

    def __getitem__(self, item):
        return getattr(self, item, None)

    def __setitem__(self, key, value):
        return setattr(self, key, value)

    # private
    def _parse_dict(self, members, hidden):
        ret = {}

        for key, value in members.items():
            if key[0] == '_' and hidden is False:
                continue
            if isinstance(value, GameObject):
                ret[key] = value.json()
            elif isinstance(value, list):
                ret[key] = self._parse_list(value)
            elif isinstance(value, dict):
                ret[key] = self._parse_dict(value, hidden)
            else:
                ret[key] = value

        return ret

    def _parse_list(self, values):
        ret = []
        for value in values:
            if isinstance(value, GameObject):
                ret.append(value.json())
            elif isinstance(value, list):
                ret.append(self._parse_list(value))
            elif isinstance(value, dict):
                ret.append(self._parse_dict(value, hidden=False))
            else:
                ret.append(value)

        return ret
