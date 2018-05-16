# -*- coding: utf-8 -*-


NAME = 'maple_guard'

HOST = '127.0.0.1'

PORT = 12555

BOX_CLASS = 'netkit.box.Box'

KEY_PREFIX = NAME + ':'

CONN_LIMIT_KEY_TPL = '{prefix}conn_limit:{node_id}:{tag}:{conn_id}:{status}'
IP_LIMIT_KEY_TPL = '{prefix}ip_limit:{node_id}#{ip}'

IP_BLOCK_KEY_TPL = '{prefix}ip_block:{node_id}#{ip}'
