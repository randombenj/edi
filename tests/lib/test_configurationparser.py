# -*- coding: utf-8 -*-
# Copyright (C) 2016 Matthias Luescher
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

from aptsources.sourceslist import SourceEntry
from edi.lib.configurationparser import ConfigurationParser, command_context


def test_project_name(config_files, config_name):
    with open(config_files, "r") as main_file:
        parser = ConfigurationParser(main_file)
        assert parser.get_configuration_name() == config_name


def test_global_configuration_overlay(config_files):
    with open(config_files, "r") as main_file:
        parser = ConfigurationParser(main_file)
        assert parser.get_compression() == "gz"
        assert parser.get_lxc_stop_timeout() == 130


def test_general_parameters(config_files):
    with open(config_files, "r") as main_file:
        parser = ConfigurationParser(main_file)
        parameters = parser.get_general_parameters()
        assert parameters.get("param1") == "keep"
        assert parameters.get("param2") == "overwritten"
        assert parameters.get("param3") == "new"


def test_bootstrap_overlay(config_files):
    with open(config_files, "r") as main_file:
        parser = ConfigurationParser(main_file)
        # the host file shall win
        boostrap_source = SourceEntry(parser.get_bootstrap_repository())
        assert parser.get_bootstrap_architecture() == "i386"
        assert "main" in boostrap_source.comps
        assert boostrap_source.uri == "http://deb.debian.org/debian/"
        # the all file shall provide this key
        expected_key = "https://ftp-master.debian.org/keys/archive-key-8.asc"
        assert parser.get_bootstrap_repository_key() == expected_key
        assert boostrap_source.dist == "jessie"
        assert parser.get_bootstrap_tool() == "debootstrap"


def test_playbooks_overlay(config_files, monkeypatch):
    with open(config_files, "r") as main_file:
        parser = ConfigurationParser(main_file)
        playbooks = parser.get_ordered_path_items("playbooks")
        assert len(playbooks) == 3
        expected_playbooks = ["10_base_system",
                              "20_networking",
                              "30_foo"]
        for playbook, expected in zip(playbooks, expected_playbooks):
            name, path, extra_vars, _ = playbook
            assert name == expected
            if name == "10_base_system":
                value = extra_vars.get("kernel_package")
                assert value == "linux-image-amd64-rt"
                value = extra_vars.get("message")
                assert value == "some message"
            if name == "20_networking":
                assert path.endswith("playbooks/foo.yml")


def test_empty_overlay_file(empty_overlay_config_file):
    with open(empty_overlay_config_file, "r") as main_file:
        parser = ConfigurationParser(main_file)
        assert parser.get_compression() == 'gz'


def test_shared_folders(config_files):
    with open(config_files, "r") as main_file:
        parser = ConfigurationParser(main_file)
        shared_folders = parser.get_ordered_raw_items('shared_folders')

        # first element
        name, content, dict = shared_folders[0]
        assert name == 'other_folder'
        assert content.get('mountpoint') == 'target_mountpoint'
        assert content.get('folder') == 'valid_folder'  # merge result
        assert dict.get('edi_current_user_host_home_directory')
        assert dict.get('edi_current_user_target_home_directory') == '/foo/bar'

        # second element
        name, content, dict = shared_folders[1]
        assert name == 'workspace'
        assert content.get('mountpoint') == 'mywork'
        assert content.get('folder') == 'work'
        assert dict.get('edi_current_user_target_home_directory').startswith('/home/')


def test_command_context():
    assert ConfigurationParser.command_context.get('edi_create_distributable_image') is False
    with command_context({'edi_create_distributable_image': True}):
        assert ConfigurationParser.command_context.get('edi_create_distributable_image') is True
        with command_context({'edi_current_context': 'bingo'}):
            assert ConfigurationParser.command_context.get('edi_create_distributable_image') is True
            assert ConfigurationParser.command_context.get('edi_current_context') == 'bingo'
            with command_context({'edi_create_distributable_image': False}):
                assert ConfigurationParser.command_context.get('edi_create_distributable_image') is False
                assert ConfigurationParser.command_context.get('edi_current_context') == 'bingo'
            assert ConfigurationParser.command_context.get('edi_create_distributable_image') is True
        assert ConfigurationParser.command_context.get('edi_create_distributable_image') is True
        assert ConfigurationParser.command_context.get('edi_current_context') is None
    assert ConfigurationParser.command_context.get('edi_create_distributable_image') is False
    assert ConfigurationParser.command_context.get('edi_current_context') is None
