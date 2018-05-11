from models.interfaces import Interface


class ICMP(Interface):

    def __init__(self)->None:
        super().__init__()
        self.name = ''
        self.dest_ip = ''
        self.reply_vl_id = ''
        self.reply_sub = ''
        self.vl_id = ''
        self.reply_vl_network_select = ''
        self.reply_vl_bag = ''
        self.reply_vl_max_frame_size = ''
        self.reply_vl_buffer_size = ''
        self.received_vl_id = ''
        self.received_vl_network_select = ''
        self.received_vl_bag = ''
        self.received_vl_skew_max = ''
        self.received_vl_integrity_checking = ''
        self.rma = ''
        self.received_vl_max_frame_size = ''
        self.received_vl_buffer_size = ''

    def _set_mandatory(self)->None:
        self._add_mandatory('dest_ip')
        self._add_mandatory('reply_vl_id')
        self._add_mandatory('reply_sub_vl_id')
        self._add_mandatory('reply_vl_buffer_size')
        self._add_mandatory('received_vl_id')
        self._add_mandatory('received_vl_buffer_size')
