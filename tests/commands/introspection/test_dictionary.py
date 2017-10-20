# -*- coding: utf-8 -*-
# Copyright (C) 2017 Matthias Luescher
#
# Authors:
#  Matthias Luescher
#
# This file is part of edi.
#
# edi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# edi is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with edi.  If not, see <http://www.gnu.org/licenses/>.

from edi.commands.imagecommands.bootstrap import Bootstrap
from edi.commands.imagecommands.imagelxc import Lxc
from edi.commands.lxccommands.export import Export
from edi.commands.lxccommands.importcmd import Import
from edi.commands.lxccommands.launch import Launch
from edi.commands.lxccommands.lxcconfigure import Configure
from edi.commands.lxccommands.profile import Profile
from edi.commands.lxccommands.publish import Publish
from edi.commands.lxccommands.stop import Stop
from edi.commands.qemucommands.fetch import Fetch
from edi.commands.targetcommands.targetconfigure import Configure as TargetConfigure
import edi
import yaml
import os
import pytest


@pytest.mark.parametrize("command, command_args", [
    (Bootstrap, ['image', 'bootstrap', '--dictionary']),
    (Lxc, ['image', 'lxc', '--dictionary']),
    (Export, ['lxc', 'export', '--dictionary']),
    (Import, ['lxc', 'import', '--dictionary']),
    (Launch, ['lxc', 'launch', '--dictionary', 'cname']),
    (Configure, ['lxc', 'configure', '--dictionary', 'cname']),
    (Profile, ['lxc', 'profile', '--dictionary']),
    (Publish, ['lxc', 'publish', '--dictionary']),
    (Stop, ['lxc', 'stop', '--dictionary']),
    (Fetch, ['qemu', 'fetch', '--dictionary']),
    (TargetConfigure, ['target', 'configure', '--dictionary', '1.2.3.4']),
])
def test_dictionary(config_files, capsys, command, command_args):
    parser = edi._setup_command_line_interface()
    command_args.append(config_files)
    cli_args = parser.parse_args(command_args)

    command().run_cli(cli_args)
    out, err = capsys.readouterr()

    assert err == ''
    dictionary = yaml.load(out)
    assert dictionary.get('edi_config_directory') == os.path.dirname(config_files)
    assert dictionary.get('edi_project_plugin_directory') == os.path.join(os.path.dirname(config_files), 'plugins')
