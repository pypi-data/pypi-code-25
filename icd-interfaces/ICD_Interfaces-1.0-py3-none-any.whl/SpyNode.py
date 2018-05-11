from typing import List, Dict

class SignalGroup:
    Application_name = ''
    Signal_name = ''
    Message_name = ''
    signals = []
    Signal_address = 0
    spy_id = 0

    def __init__(self, item:str)->None:
        self.signals: List[] = []
        self.Application_name = item.Application_name
        self.Message_name = item.Message_name
        self.Signal_name = item.Functional_Status_name.replace("FS_","")
        self.spy_id = 0
        self.Signal_address = item.Signal_address

    def add_signal(self, signal: str)->None:
        self.signals.append(signal)

    def get_signal_names(self)->None:
        names:List[str] = []
        for signal in self.signals:
            names.append(signal.Signal_name)
        return names


class AfdxMessage:
    messages = []
    message_names = []

    def __init__(self)->None:
        self.message_names = []
        self.messages = []

    def sort_messages(self)->None:
        for message in self.messages:
            message.sort_children()

    def find(self, item.str)->None:
        if item.Message_name in self.message_names:
            self.messages[self.message_names.index(item.Message_name)].add_children(item)
        else:
            self.message_names.append(item.Message_name)
            self.messages.append(SingleAfdxMessage(item.Message_name))

class SingleAfdxMessage:
    name = ''
    children = []
    children_names = []
    message_length = 0

    def __init__(self, name:str)->None:
        self.name = name
        self.children_names = []
        self.children = []
        self.message_length = 0

    def add_children(self, item:str)->None:
        self.message_length = int(int(item.Message_length)/4)
#        if not item.Signal_name in self.children_names:
        if len(item.Signal_position) > 0 and item.Functional_Status_name in self.children_names:
            self.children[self.children_names.index(item.Functional_Status_name)].add_signal(item)
        elif len(item.Signal_position) == 0:
            self.children_names.append(item.Signal_name)
            self.children.append(SingleSignal(item))
        else:
            self.children_names.append(item.Functional_Status_name)
            self.children.append(SignalGroup(item))

    def sort_children(self)->None:
        l = []
        for i in range(0, self.message_length):
            l.append(AfdxSpare(i))
        for child in self.children:
            idx = int(int(child.Signal_address) / 4)
            child.spy_id = idx*5
            l[idx] = child
        self.children = l


class AfdxSpare:
    spy_id = 0

    def __init__(self, spy_id:str)->None:
        self.spy_id = spy_id

class SingleSignal:

    Application_name = ''
    Signal_name = ''
    signals = ''
    Message_name = ''
    Signal_address = 0
    spy_id = 0

    def __init__(self, item:str)->None:
        self.Signal_name = item.Signal_name
        self.Application_name = item.Application_name
        self.signals = [item]
        self.Message_name = item.Message_name
        self.spy_id = 0
        self.Signal_address = item.Signal_address

    def get_signal_names(self)->None:
        return [self.Signal_name]

class AfdxGroup:
    signal_group_names = []
    signal_groups = []
    spy_id = 0

    def __init__(self)->None:
        self.signal_group_names = []
        self.signal_groups = []
        self.spy_id = 0

    def find(self, item:str)->None:
        if item.Functional_Status_name in self.signal_group_names and len(item.Signal_position)>0:
            self.signal_groups[self.signal_group_names.index(item.Functional_Status_name)].add_signal(item)
        elif len(item.Signal_position)==0:
            self.signal_group_names.append(item.Signal_name)
            self.signal_groups.append(SingleSignal(item))
        else:
            self.signal_group_names.append(item.Functional_Status_name)
            self.signal_groups.append(SignalGroup(item))

class NodeGroup:
    keys = ['RESERVED', 'FS', 'VALUE', 'VALID', 'RETURN_CODE']
    children = []
    name = ''
    sortingkey = ''
    type = ''
    comment = False

    def __init__(self)->None:
        self.children = []
        self.name = ''
        self.sortingkey = ''
        self.type = ''
        self.comment = False

    def add_sortingkey(self, laneid:str, modulename:str, moduleid:str, moduletype:str, sideid:str, laneindex:str)->None:
        sorting = SortingKey()
        sorting.LaneID = laneid
        sorting.ModuleName = modulename
        sorting.ModuleID = moduleid
        sorting.ModuleType = moduletype
        sorting.SideID = sideid
        sorting.LaneIndex = laneindex
        self.sortingkey = sorting

    def create_group(self, name:str, start_value:int)->str:
        self.name = name
        i = start_value
        for key in self.keys:
            node = False
            node = Node()
            node.name = name + '_' + key
            node.sortingkey = self.sortingkey

            node.add_property_spy(i)
            node.add_property_laneid(self.sortingkey.LaneID)
            node.add_property_ui()

            self.children.append(node)
            i += 1
        return i


class Node:
    properties = []
    name = ''
    sortingkey = ''

    def __init__(self)->None:
        self.properties = []
        self.name = ''
        self.sortingkey = ''

    def add_property_spy(self, initval:str)->None:
        prop = Property()
        prop.name = 'SPYID'
        prop.dtype = 'ST'
        prop.togreaten = 'FALSE'
        prop.static = 'TRUE'
        prop.greatennode = 'SPY'
        prop.initval = str(initval)
        self.properties.append(prop)

    def add_property_ui(self)->None:
        prop = Property()
        prop.name = ''
        prop.dtype = 'UI'
        prop.togreaten = 'TRUE'
        prop.static = 'FALSE'
        prop.greatennode = 'SPY'
        prop.initval = '12345'
        self.properties.append(prop)

    def add_property_laneid(self, laneid:str)->None:
        prop = Property()
        prop.name = 'LANEID'
        prop.dtype = 'ST'
        prop.togreaten = 'FALSE'
        prop.static = 'TRUE'
        prop.greatennode = 'SPY'
        prop.initval = str(laneid)
        self.properties.append(prop)

class Property:
    name = ''
    dtype = ''
    togreaten = ''
    static = ''
    greatennode = ''
    initval = ''

    def __init__(self)->None:
        self.name = ''
        self.dtype = ''
        self.togreaten = ''
        self.static = ''
        self.greatennode = ''
        self.initval = ''

    def get_attributes(self)->Dict{}:
        return {'NAME': self.name, 'DTYPE': self.dtype, 'TOGREATEN': self.togreaten, 'STATIC': self.static,
                'GREATENNODE': self.greatennode, 'INITVAL': self.initval}

class SortingKey:
    LaneID = ''
    ModuleName = ''
    ModuleID = ''
    ModuleType = ''
    SideID = ''
    LaneIndex = ''

    def __init__(self)->None:
        self.LaneID = ''
        self.ModuleName = ''
        self.ModuleID = ''
        self.ModuleType = ''
        self.SideID = ''
        self.LaneIndex = ''

    def get_attributes(self)->Dict{}:
        return {'LaneID': str(self.LaneID), 'ModuleName': str(self.ModuleName), 'ModuleID': str(self.ModuleID),
                'ModuleType': str(self.ModuleType), 'SideID': str(self.SideID), 'LaneIndex': str(self.LaneIndex)}
