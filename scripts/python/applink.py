# coding=utf8

# ===== applink.py
#
# Copyright (c) 2022 Artur J. Żarek
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License

import hou
import sys
import hrpyc
import xmlrpc.client
from pathlib import PurePath


def houdini_export():
    sops = hou.selectedNodes()

    if len(sops) == 0:
        hou.ui.displayMessage('Nothing to export!',
                              severity=hou.severityType.Error)
        sys.exit(1)

    HOST = 'localhost'
    PORT = 8000

    # Check if RPC server exists
    s = xmlrpc.client.ServerProxy(f'http://{HOST}:{PORT}')

    try:
        s.system.listMethods()
    except ConnectionRefusedError:
        hou.ui.displayMessage('Could not connect to RPC server.',
                              severity=hou.severityType.Error)
        sys.exit(2)

    # Export selected geometry.
    for sop in sops:
        abc = sop.parent().createNode('rop_alembic')
        abc.setFirstInput(sop)

        filename = sop.name() + '.abc'
        filepath = PurePath(hou.text.expandString("$TEMP"), filename)
        abc.setParms({
            'filename': str(filepath),
            'build_from_path': 1,
            'path_attrib': 'name'
        })
        abc.parm('execute').pressButton()

        s.import_alembic(str(filepath))
        abc.destroy()


if __name__ == '__main__':
    houdini_export()
