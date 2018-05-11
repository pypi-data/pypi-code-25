class NodeEth:

    AfdxFrames = ['RSET', 'ERPQ', 'EIPC', 'ESAP']  #... extend
    children = []
    full_name = ''
    name = ''
    type = 'NODE'

    def build(self, name:str)-> str:
        self.name = name
        self.full_name = 'NODE_ETH_'+name
        for frame in self.AfdxFrames:
            frameObject = AfdxFrame()
            frameObject.build(self, frame)
            self.children.append(frameObject)
        return self

class AfdxFrame:
    children = []
    Arrays = ['FLAGS', 'SIGNAL01', 'SIGNAL02', 'SIGNAL03', 'SIGNAL04', 'SIGNAL05', 'SIGNAL06', 'SIGNAL07', 'SIGNAL08',
              'SIGNAL09', 'SIGNAL10', 'SIGNAL11', 'SIGNAL12', 'SIGNAL13', 'SIGNAL14', 'SIGNAL15', 'SIGNAL16',
              'SIGNAL17', 'SIGNAL18', 'SIGNAL19', 'SIGNAL20']
    name = ''
    full_name = ''
    type = False
    attributes = ['Header_Length', 'Differentiated_Services_Field','Total_Length', 'Identification', 'Flags',
                  'Fragment_Offset', 'Time_To_Live', 'Protocol', 'Header_Checksum', 'Source', 'Destination']

    def build(self, parent:str, name:str)->str:
        self.full_name = 'NODE_ETH.' + parent.name + '.CONFIG.AFDXFRAME_' + name
        self.name = name
        for array in self.Arrays:
            arrayObject = ArrayFlag()
            arrayObject.build(self, array)
            self.children.append(arrayObject)

        return self.children

    def create_attributes(self, name:str)->object:
        data = dict()
        data['NAME'] = name
        data['DIM'] = ""
        data['DTYPE'] = "UL"
        data['INITVAL'] = '0'
        data['VISPR'] = ""
        data['DESC'] = ""

        return data

class ArrayFlag:
    Flags = ['CommigFlag', 'SendFlag', 'ReceiveFlag', 'isCyclic', 'CycleTime', 'BurstMode', 'NumofBurstFrames', 'Phase',
         'IP_HeaderChecksum_autocalc', 'AFDX_SeqNum_autocalc', 'ActiveChannels', 'Burst_VL_ID_Start',
         'Burst_VL_ID_Stop', 'IgnorePayload', 'ReceiveTime', 'UseFragmentation', 'UsePayloadCheck', 'AFDX_SeqNum']

    Signals = ['SigName', 'isFile', 'startbyte', 'startbit', 'stopbit']

    name = ''
    full_name = ''
    children = []
    type = 'ARRAY'

    def build(self, parent:str, name:str)->None:
        self.name = name
        self.full_name = parent.full_name + '.' + name
        if name == 'FLAGS':
            for flag in self.Flags:
                elementObject = Element()
                elementObject.build(self, flag)
                self.children.append(elementObject)

class Element:

    Attributes = ['NAME', 'DIM', 'DTYPE', 'INITVAL', 'VISPR', 'DESC']

    name = ''
    full_name = ''
    type = 'ELEMENT'

    def build(self, parent:str, name:str)->None:
        self.name = name
        #return self.Attributes
        #for attribute in self.Attributes:

            #print(attribute)