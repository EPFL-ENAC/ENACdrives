#!/usr/bin/env python3

# Bancal Samuel

# Tests conf.py


import io
import unittest
from utility import Output
from conf import read_config_source


class TestConfMethods(unittest.TestCase):
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
                {'global': {'Linux_CIFS_method': 'gvfs'}}
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
                    {'CIFS_mount': [{'name': 'test'}]}
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
                {'CIFS_mount': [{'name': 'test',
                                 'server_path': 'data/foo',
                                 'local_path': '/home/user/Desktop/mnt', }]}
            )
            s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])

    def test_bool_false(self):
        for s in ("non", "foobar", "false", "FALSE", "NO", "0"):
            s_in = io.StringIO("""
[CIFS_mount]
name = test
stared = {0}
""".format(s))
            s_out = io.StringIO("")
            with Output(dest=s_out):
                self.assertEqual(
                    read_config_source(s_in),
                    {'CIFS_mount': [{'name': 'test',
                                     "stared": False, }]}
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
                    {'CIFS_mount': [{'name': 'test',
                                     "Linux_gvfs_symlink": True, }]}
                )
                s_out.seek(0)
            self.assertEqual(s_out.readlines(), [])


if __name__ == '__main__':
    unittest.main()
