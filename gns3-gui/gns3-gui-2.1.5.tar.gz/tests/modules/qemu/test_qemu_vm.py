# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from unittest.mock import patch, Mock, ANY
from gns3.modules.qemu.qemu_vm import QemuVM
from gns3.ports.port import Port
from gns3.base_node import BaseNode


def test_qemu_vm_init(local_server, project):

    vm = QemuVM(None, local_server, project)


def test_update(qemu_vm):

    new_settings = {
        "name": "QEMU2",
    }

    with patch('gns3.base_node.BaseNode.controllerHttpPut') as mock:
        qemu_vm.update(new_settings)

        assert mock.called
        args, kwargs = mock.call_args
        assert args[0] == "/nodes/{node_id}".format(node_id=qemu_vm.node_id())
        assert kwargs["body"] == {
            'node_id': qemu_vm._node_id,
            'compute_id': 'local',
            'name': 'QEMU2', 'node_type': 'qemu', 'properties': {}}

        # Callback
        args[1]({"name": "QEMU2"})
