#!/usr/bin/env python3

# Bancal Samuel

# Tests conf.py


import io
import copy
import unittest
from utility import Output
from conf import read_config_source, validate_config, merge_configs, ConfigException


class TestReadConfigSource(unittest.TestCase):
    def test_empty(self):
        s_in = io.StringIO("")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(read_config_source(s_in), {})
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_comment(self):
        s_in = io.StringIO("""
# one two
[global]  # foo
Linux_CIFS_method = gvfs  # bar
# hello
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {"global": {"Linux_CIFS_method": "gvfs"}}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_unknown_section(self):
        s_in = io.StringIO("""
[glob]
Linux_CIFS_method = gvfs
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            with self.assertRaises(ConfigException):
                self.assertEqual(
                    read_config_source(s_in),
                    {}
                )
            s_out.seek(0)
            self.assertIn("Unexpected section", s_out.readlines()[0])

    def test_unknown_option(self):
        s_in = io.StringIO("""
[global]
Linux_CIFS_meth = gvfs
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {}
            )
            s_out.seek(0)
            self.assertIn("Unexpected option", s_out.readlines()[0])

    def test_bad_option(self):
        s_in = io.StringIO("""
[global]
name = test
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {}
            )
            s_out.seek(0)
            self.assertIn("Unexpected option", s_out.readlines()[0])

    def test_bad_servername(self):
        for s in ("'hello", "with_underscore", "&foo"):
            s_in = io.StringIO("""
[CIFS_mount]
name = test
server_name = {0}
""".format(s))
            s_out = io.StringIO("")
            with Output(dest=s_out):
                self.assertEqual(
                    read_config_source(s_in),
                    {"CIFS_mount": {"test": {}}}
                )
                s_out.seek(0)
                self.assertIn("server_name can only contain", s_out.readlines()[0])

    def test_path(self):
        s_in = io.StringIO(r"""
[CIFS_mount]
name = test
server_path = data\foo
local_path = \home\user\Desktop\mnt
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {"CIFS_mount": {"test": {
                                 "server_path": "data/foo",
                                 "local_path": "/home/user/Desktop/mnt", }}}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_bool_false(self):
        for s in ("non", "foobar", "false", "FALSE", "NO", "0"):
            s_in = io.StringIO("""
[CIFS_mount]
name = test
bookmark = {0}
""".format(s))
            s_out = io.StringIO("")
            with Output(dest=s_out):
                self.assertEqual(
                    read_config_source(s_in),
                    {"CIFS_mount": {"test": {
                                     "bookmark": False, }}}
                )
                s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_bool_true(self):
        for s in ("yes", "y", "true", "True", "TRUE", "1"):
            s_in = io.StringIO("""
[CIFS_mount]
name = test
Linux_gvfs_symlink = {0}
""".format(s))
            s_out = io.StringIO("")
            with Output(dest=s_out):
                self.assertEqual(
                    read_config_source(s_in),
                    {"CIFS_mount": {"test": {
                                     "Linux_gvfs_symlink": True, }}}
                )
                s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_complete_cifs_mount_entry(self):
        s_in = io.StringIO(r"""
[CIFS_mount]
name = test
server_path = data\foo
local_path = \home\user\Desktop\mnt
""")
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {"CIFS_mount": {"test": {
                                 "server_path": "data/foo",
                                 "local_path": "/home/user/Desktop/mnt", }}}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_complete_config(self):
        s_in = io.StringIO(r"""
[global]
username = bancal
Linux_CIFS_method = gvfs
Linux_mountcifs_filemode = 0770
Linux_mountcifs_dirmode = 0770
Linux_mountcifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
Linux_gvfs_symlink = true

[msg]
name = one msg to show up
text = Hello user
icon = info

[msg]
name = second msg to show up
text = Be careful!
icon = warning

[msg]
name = 3rd msg
text = third with no icon

[network]
name = Internet
ping = www.epfl.ch
ping = www.enacit.epfl.ch
error_msg = Error, you are not connected to the network. You won't be able to mount this resource.

[network]
name = Epfl
parent = Internet
cifs = files0.epfl.ch
cifs = files1.epfl.ch
cifs = files8.epfl.ch
cifs = files9.epfl.ch
cifs = enac1files.epfl.ch
error_msg = Error, you are not connected to the intranet of EPFL. Run a VPN client to be able to mount this resource.

[realm]
name = EPFL
domain = INTRANET
username = bancal

[CIFS_mount]
name = private
label = bancal@files9
require_network = Epfl
realm = EPFL
server_name = files9.epfl.ch
server_path = data/bancal
local_path = {MNT_DIR}/bancal_on_files9
#    {MNT_DIR}
#    {HOME_DIR}
#    {DESKTOP_DIR}
#    {LOCAL_USERNAME}
#    {LOCAL_GROUPNAME}
bookmark = false
#    default : False
Linux_CIFS_method = gvfs
#    mount.cifs : Linux's mount.cifs (requires sudo ability)
#    gvfs : Linux's gvfs-mount
Linux_mountcifs_filemode = 0770
Linux_mountcifs_dirmode = 0770
Linux_mountcifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
Linux_gvfs_symlink = yes
#    Enables the creation of a symbolic link to "local_path" after mount with gvfs method.
#    default : True
Windows_letter = Z:
#    Drive letter to use for the mount
""")
        s_out = io.StringIO("")
        self.maxDiff = None
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {'CIFS_mount': {
                  'private': {
                   'require_network': 'Epfl',
                   'Linux_CIFS_method': 'gvfs',
                   'Linux_gvfs_symlink': True,
                   'Linux_mountcifs_dirmode': '0770',
                   'Linux_mountcifs_filemode': '0770',
                   'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm',
                   'Windows_letter': 'Z:',
                   'label': 'bancal@files9',
                   'local_path': '{MNT_DIR}/bancal_on_files9',
                   'realm': 'EPFL',
                   'server_name': 'files9.epfl.ch',
                   'server_path': 'data/bancal',
                   'bookmark': False}},
                 'global': {
                  'username': 'bancal',
                  'Linux_CIFS_method': 'gvfs',
                  'Linux_gvfs_symlink': True,
                  'Linux_mountcifs_dirmode': '0770',
                  'Linux_mountcifs_filemode': '0770',
                  'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm'},
                 'network': {
                  'Epfl': {
                   'error_msg': 'Error, you are not connected to the '
                                'intranet of EPFL. Run a VPN client to '
                                'be able to mount this resource.',
                   'parent': 'Internet',
                   'cifs': [
                    'files0.epfl.ch',
                    'files1.epfl.ch',
                    'files8.epfl.ch',
                    'files9.epfl.ch',
                    'enac1files.epfl.ch']},
                  'Internet': {
                   'error_msg': 'Error, you are not connected to '
                                "the network. You won't be able to "
                                'mount this resource.',
                   'ping': [
                    'www.epfl.ch',
                    'www.enacit.epfl.ch']}},
                 'realm': {
                  'EPFL': {
                   'domain': 'INTRANET',
                   'username': 'bancal'}},
                 'msg': {
                  'one msg to show up': {'icon': 'info', 'text': 'Hello user'},
                  'second msg to show up': {'icon': 'warning', 'text': 'Be careful!'},
                  '3rd msg': {'text': 'third with no icon'}},}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_complete_config2(self):
        s_in = io.StringIO(r"""
[global]
username = bancal
Linux_CIFS_method = gvfs
Linux_mountcifs_filemode = 0770
Linux_mountcifs_dirmode = 0770
Linux_mountcifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
Linux_gvfs_symlink = true
require_network = EPFL-Intranet
realm = EPFL-AD

[realm]
name = EPFL-AD
domain = INTRANET
username = bancal

[network]
name = Internet
ping = www.epfl.ch
ping = enacit.epfl.ch
ping = enclair.epfl.ch
error_msg = Error, you are not connected to the network. You won't be able to connect to this resource.

[network]
name = EPFL-Intranet
parent = Internet
cifs = files0.epfl.ch
cifs = files1.epfl.ch
cifs = files8.epfl.ch
cifs = files9.epfl.ch
cifs = enac1files.epfl.ch
error_msg = Error, you are not connected to the intranet of EPFL. Run a VPN client to be able to connect to this resource.

[CIFS_mount]
name = private
label = bancal@files9
unc = //files9.epfl.ch/data/bancal
local_path = {MNT_DIR}/bancal_on_files9
""")
        s_out = io.StringIO("")
        self.maxDiff = None
        with Output(dest=s_out):
            self.assertEqual(
                read_config_source(s_in),
                {'CIFS_mount': {
                  'private': {
                   'label': 'bancal@files9',
                   'local_path': '{MNT_DIR}/bancal_on_files9',
                   'unc': '//files9.epfl.ch/data/bancal', }},
                 'global': {
                  'username': 'bancal',
                  'realm': 'EPFL-AD',
                  'require_network': 'EPFL-Intranet',
                  'Linux_CIFS_method': 'gvfs',
                  'Linux_gvfs_symlink': True,
                  'Linux_mountcifs_dirmode': '0770',
                  'Linux_mountcifs_filemode': '0770',
                  'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm'},
                 'network': {
                  'EPFL-Intranet': {
                   'error_msg': 'Error, you are not connected to the intranet '
                                'of EPFL. Run a VPN client to be able to '
                                'connect to this resource.',
                   'parent': 'Internet',
                   'cifs': [
                    'files0.epfl.ch',
                    'files1.epfl.ch',
                    'files8.epfl.ch',
                    'files9.epfl.ch',
                    'enac1files.epfl.ch']},
                  'Internet': {
                   'error_msg': 'Error, you are not connected to the network. '
                                "You won't be able to connect to this resource.",
                   'ping': [
                    'www.epfl.ch',
                    'enacit.epfl.ch',
                    'enclair.epfl.ch']}},
                 'realm': {
                  'EPFL-AD': {
                   'domain': 'INTRANET',
                   'username': 'bancal'}}}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])


class TestValidateConfig(unittest.TestCase):
    def test_empty(self):
        cfg = {}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), {})
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_basic_cifs_mount(self):
        cfg = {"CIFS_mount": {
                "name": {
                 "label": "label",
                 "realm": "r_name",
                 "server_name": "server_name",
                 "server_path": "server_path",
                 "local_path": "local_path", }},
               "realm": {
                "r_name": {
                 "username": "u",
                 "domain": "d", }}}
        cfg_expected = copy.deepcopy(cfg)
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_incomplete_cifs_mount(self):
        cfg = {"CIFS_mount": {
                "name": {
                 "label": "label",
                 "realm": "realm",
                 # "server_name": "server_name",
                 "server_path": "server_path",
                 "local_path": "local_path", }},
                "realm": {
                 "r_name": {
                  "username": "u",
                  "domain": "d", }}}
        cfg_expected = {"CIFS_mount": {},
                        "realm": {
                         "r_name": {
                          "username": "u",
                          "domain": "d", }}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertIn("expected 'server_name' option in CIFS_mount section.", s_out.readlines()[0])

    def test_missing_realm(self):
        cfg = {"CIFS_mount": {
                "name": {
                 "label": "label",
                 "realm": "r_name",
                 "server_name": "server_name",
                 "server_path": "server_path",
                 "local_path": "local_path", }}}
        cfg_expected = {"CIFS_mount": {}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [
                "ERROR: Missing realm 'r_name'.\n",
                "ERROR: Removing CIFS_mount 'name' depending on realm 'r_name'.\n"])

    def test_incomplete_network(self):
        self.maxDiff = None
        cfg = {'network': {
                'Epfl': {
                 'error_msg': 'Error, you are not connected to the '
                              'intranet of EPFL. Run a VPN client to '
                              'be able to mount this resource.',
                 'parent': 'Internet'}}}
        cfg_expected = {"network": {}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [
                "ERROR: expected 'ping' or 'cifs' option in network section.\n",
                "ERROR: Removing incomplete network 'Epfl'.\n"])

    def test_incomplete_dependency_network(self):
        cfg = {'network': {
                'Epfl': {
                 'error_msg': 'Error, you are not connected to the '
                              'intranet of EPFL. Run a VPN client to '
                              'be able to mount this resource.',
                 'parent': 'Internet',
                 'ping': [
                  'files0.epfl.ch',
                  'files1.epfl.ch',
                  'files8.epfl.ch',
                  'files9.epfl.ch']}}}
        cfg_expected = {'network': {}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_complete_network(self):
        cfg = {'network': {
                'Epfl': {
                 'error_msg': 'Error, you are not connected to the '
                              'intranet of EPFL. Run a VPN client to '
                              'be able to mount this resource.',
                 'parent': 'Internet',
                 'ping': [
                  'files0.epfl.ch',
                  'files1.epfl.ch',
                  'files8.epfl.ch',
                  'files9.epfl.ch']},
                'Internet': {
                 'error_msg': 'Error, you are not connected to the Internet',
                 'ping': [
                  'www.epfl.ch',
                  'enacit.epfl.ch']}}}
        cfg_expected = copy.deepcopy(cfg)
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_incomplete_msg1(self):
        cfg = {"msg": {"1st": {"no-text": "bla"}}}
        cfg_expected = {"msg": {}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [
                "ERROR: expected 'text' option in msg section.\n",
                "ERROR: Removing incomplete msg '1st'.\n"])

    def test_incomplete_msg2(self):
        cfg = {"msg": {"1st": {"text": "bla"}}}
        cfg_expected = {"msg": {"1st": {"text": "bla", "icon": "none"}}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_complete_config(self):
        self.maxDiff = None
        cfg = {'CIFS_mount': {
                'private': {
                 'label': 'bancal@files9',
                 'unc': '//files9.epfl.ch/data/bancal', }},
               'global': {
                'username': 'bancal',
                'realm': 'EPFL-AD',
                'require_network': 'EPFL-Intranet',
                'Linux_CIFS_method': 'gvfs',
                'Linux_gvfs_symlink': True,
                'Linux_mountcifs_dirmode': '0770',
                'Linux_mountcifs_filemode': '0770',
                'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm'},
               'network': {
                'EPFL-Intranet': {
                 'error_msg': 'Error, you are not connected to the intranet '
                              'of EPFL. Run a VPN client to be able to '
                              'connect to this resource.',
                 'parent': 'Internet',
                 'cifs': [
                  'files0.epfl.ch',
                  'files1.epfl.ch',
                  'files8.epfl.ch',
                  'files9.epfl.ch',
                  'enac1files.epfl.ch']},
                'Internet': {
                 'error_msg': 'Error, you are not connected to the network. '
                              "You won't be able to connect to this resource.",
                 'ping': [
                  'www.epfl.ch',
                  'enacit.epfl.ch',
                  'enclair.epfl.ch']}},
               'realm': {
                'EPFL-AD': {
                 'domain': 'INTRANET',
                 'username': 'bancal'}}}

        cfg_expected = copy.deepcopy(cfg)
        cfg_expected["CIFS_mount"]["private"]["server_name"] = "files9.epfl.ch"
        cfg_expected["CIFS_mount"]["private"]["server_path"] = "data/bancal"
        cfg_expected["CIFS_mount"]["private"]["local_path"] = "{MNT_DIR}/private"
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(cfg), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])


class TestReadAndValidateConfig(unittest.TestCase):

    def test_complete_config(self):
        self.maxDiff = None
        s_in = io.StringIO(r"""
[global]
username = bancal
Linux_CIFS_method = gvfs
Linux_mountcifs_filemode = 0770
Linux_mountcifs_dirmode = 0770
Linux_mountcifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
Linux_gvfs_symlink = true
require_network = EPFL-Intranet
realm = EPFL-AD

[msg]
name = simple message
text = this is a message

[realm]
name = EPFL-AD
domain = INTRANET
username = bancal

[network]
name = Internet
ping = www.epfl.ch
ping = enacit.epfl.ch
ping = enclair.epfl.ch
error_msg = Error, you are not connected to the network. You won't be able to connect to this resource.

[network]
name = EPFL-Intranet
parent = Internet
cifs = files0.epfl.ch
cifs = files1.epfl.ch
cifs = files8.epfl.ch
cifs = files9.epfl.ch
cifs = enac1files.epfl.ch
error_msg = Error, you are not connected to the intranet of EPFL. Run a VPN client to be able to connect to this resource.

[CIFS_mount]
name = private
unc = //files9.epfl.ch/data/bancal

[CIFS_mount]
name = private2
unc = \\files9.epfl.ch\data\bancal
""")

        cfg_expected = {'CIFS_mount': {
                'private': {
                 'label': 'private',
                 'unc': '//files9.epfl.ch/data/bancal',
                 "server_name": "files9.epfl.ch",
                 "server_path": "data/bancal",
                 "local_path": "{MNT_DIR}/private"},
                'private2': {
                 'label': 'private2',
                 'unc': '//files9.epfl.ch/data/bancal',
                 "server_name": "files9.epfl.ch",
                 "server_path": "data/bancal",
                 "local_path": "{MNT_DIR}/private2"},
                 },
               'global': {
                'username': 'bancal',
                'realm': 'EPFL-AD',
                'require_network': 'EPFL-Intranet',
                'Linux_CIFS_method': 'gvfs',
                'Linux_gvfs_symlink': True,
                'Linux_mountcifs_dirmode': '0770',
                'Linux_mountcifs_filemode': '0770',
                'Linux_mountcifs_options': 'rw,nobrl,noserverino,iocharset=utf8,sec=ntlm'},
               'network': {
                'EPFL-Intranet': {
                 'error_msg': 'Error, you are not connected to the intranet '
                              'of EPFL. Run a VPN client to be able to '
                              'connect to this resource.',
                 'parent': 'Internet',
                 'cifs': [
                  'files0.epfl.ch',
                  'files1.epfl.ch',
                  'files8.epfl.ch',
                  'files9.epfl.ch',
                  'enac1files.epfl.ch']},
                'Internet': {
                 'error_msg': 'Error, you are not connected to the network. '
                              "You won't be able to connect to this resource.",
                 'ping': [
                  'www.epfl.ch',
                  'enacit.epfl.ch',
                  'enclair.epfl.ch']}},
               'realm': {
                'EPFL-AD': {
                 'domain': 'INTRANET',
                 'username': 'bancal'}},
                'msg': {'simple message': {'icon': 'none', 'text': 'this is a message'}}}

        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(validate_config(read_config_source(s_in)), cfg_expected)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])


class TestMergeConfigs(unittest.TestCase):
    def test_empty(self):
        cfg = {}
        cfg_to_merge = {}
        expected_cfg = {
            'CIFS_mount': {},
            'global': {'entries_order': []},
            'realm': {},
            'network': {},
            'msg': {}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(merge_configs(cfg, cfg_to_merge), expected_cfg)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_yes_no(self):
        cfg = {'global': {'entries_order': ["a", "b"]}}
        cfg_to_merge = {}
        expected_cfg = {
            'CIFS_mount': {},
            'global': {'entries_order': ["a", "b"]},
            'realm': {},
            'network': {},
            'msg': {}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(merge_configs(cfg, cfg_to_merge), expected_cfg)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_no_yes(self):
        cfg = {}
        cfg_to_merge = {'global': {'entries_order': ["a", "b"]}}
        expected_cfg = {
            'CIFS_mount': {},
            'global': {'entries_order': ["a", "b"]},
            'realm': {},
            'network': {},
            'msg': {}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(merge_configs(cfg, cfg_to_merge), expected_cfg)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_yes_yes(self):
        cfg = {'global': {'entries_order': ["a", "b", "c", "d"]}}
        cfg_to_merge = {'global': {'entries_order': ["c", "a"]}}
        expected_cfg = {
            'CIFS_mount': {},
            'global': {'entries_order': ["c", "a", "b", "d"]},
            'realm': {},
            'network': {},
            'msg': {}}
        s_out = io.StringIO("")
        with Output(dest=s_out):
            self.assertEqual(merge_configs(cfg, cfg_to_merge), expected_cfg)
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])


if __name__ == "__main__":
    unittest.main()
