% ENACdrives
% enac.epfl.ch - Samuel Bancal


2015.01.19 - SB ● Python Qt4
--------------------------------------------------------------------------------

Installed System wide because couldn't find PyQt4 in pip

~~~ bash
sudo apt-get install python3-pyqt4
~~~


2018-04-12 - SB ● Pipenv
--------------------------------------------------------------------------------

```bash
cd ~/Projects/enacdrives/client
pipenv install --three
export PYTHONPATH=/usr/lib/python3/dist-packages
pipenv run python enacdrives.py
```


2015.01.19 - SB ● Linux cx_Freeze (compile Python to executables)
--------------------------------------------------------------------------------

Installing with pip gives

~~~ out
[...]
collect2: error: ld returned 1 exit status
error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
[...]
~~~

Installing System wide is only for Python2

Installing by hand (following patch described here <http://stackoverflow.com/a/25119820/446302>)

~~~ bash
mkdir dependencies
cd dependencies/
wget https://pypi.python.org/packages/source/c/cx_Freeze/cx_Freeze-4.3.4.tar.gz#md5=5bd662af9aa36e5432e9144da51c6378
tar -xf cx_Freeze-4.3.4.tar.gz
cd cx_Freeze-4.3.4/
less README.txt
. ../../venv_py3/bin/activate
python setup.py build
~~~

~~~ out
collect2: error: ld returned 1 exit status
error: command 'x86_64-linux-gnu-gcc' failed with exit status 1
~~~

~~~ bash
vi setup.py
~~~

~~~ snip
# if not vars.get("Py_ENABLE_SHARED", 0):
if True:
~~~

~~~ bash
python setup.py build
python setup.py install
pip freeze --local
~~~

~~~ out
cx-Freeze==4.3.4
~~~


2015.02.02 - SB ● cx_Freeze Install on MacOSX (not used)
--------------------------------------------------------------------------------

1. Install Xcode
2. Launch Xcode to agree the licence
3. Install Anaconda3 64b from http://continuum.io/downloads#py34
4. pip install cx_Freeze
   FAILED !!!


2015.02.19 - SB ● Windows install winpexpect (not used)
--------------------------------------------------------------------------------

~~~ cmd
pip install winpexpect
~~~


2015.03.24 - SB ● MacOSX install py2app
--------------------------------------------------------------------------------

~~~ cmd
pip install py2app
~~~


2015.03.24 - SB ● MacOSX created enacdrives.icns (icon set)
--------------------------------------------------------------------------------

Instructions at http://applehelpwriter.com/2012/12/16/make-your-own-icns-icons-for-free/

create Folder "enacdrives.iconset" (accept the extension ".iconset")
With image preview, save 10 files in that folder :

* icon_16x16.png (= 16 x 16)
* icon_16x16@2x.png (= 32 x 32)
* icon_32x32.png (= 32 x 32)
* icon_32x32@2x.png (= 64 x 64)
* icon_128x128.png (= 128 x 128)
* icon_128x128@2x.png (= 256 x 256)
* icon_256x256.png (= 256 x 256)
* icon_256x256@2x.png (= 512 x 512)
* icon_512x512.png (= 512 x 512)
* icon_512x512@2x.png (= 1024 x 1024)

In Terminal, run :

iconutil -c icns enacdrives.iconset

scp enacdrives.icns sbancal@salsa:Drop


2015.03.24 - SB ● Create enacdrives.app
--------------------------------------------------------------------------------

py2applet --make-setup enacdrives.py enacdrives.icns

This creates a setup.py ... rename it to setup_osx.py

python setup_osx.py py2app

1) This fails with :
Traceback (most recent call last):
  File "setup_osx.py", line 21, in <module>
    setup_requires=['py2app'],
  File "/Users/bancal/anaconda/lib/python3.4/distutils/core.py", line 148, in setup
    dist.run_commands()
  File "/Users/bancal/anaconda/lib/python3.4/distutils/dist.py", line 955, in run_commands
    self.run_command(cmd)
  File "/Users/bancal/anaconda/lib/python3.4/distutils/dist.py", line 974, in run_command
    cmd_obj.run()
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/py2app/build_app.py", line 659, in run
    self._run()
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/py2app/build_app.py", line 865, in _run
    self.run_normal()
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/py2app/build_app.py", line 959, in run_normal
    self.create_binaries(py_files, pkgdirs, extensions, loader_files)
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/py2app/build_app.py", line 1205, in create_binaries
    mm.mm.run_file(runtime)
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/macholib/MachOGraph.py", line 81, in run_file
    raise ValueError('%r does not exist' % (pathname,))
ValueError: '/Users/bancal/anaconda/lib/libpython3.4.dylib' does not exist

Workaround :
ln -s libpython3.4m.dylib /Users/bancal/anaconda/lib/libpython3.4.dylib

2) fails with :
Traceback (most recent call last):
  File "setup_osx.py", line 21, in <module>
    setup_requires=['py2app'],
  File "/Users/bancal/anaconda/lib/python3.4/distutils/core.py", line 148, in setup
    dist.run_commands()
  File "/Users/bancal/anaconda/lib/python3.4/distutils/dist.py", line 955, in run_commands
    self.run_command(cmd)
  File "/Users/bancal/anaconda/lib/python3.4/distutils/dist.py", line 974, in run_command
    cmd_obj.run()
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/py2app/build_app.py", line 659, in run
    self._run()
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/py2app/build_app.py", line 865, in _run
    self.run_normal()
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/py2app/build_app.py", line 959, in run_normal
    self.create_binaries(py_files, pkgdirs, extensions, loader_files)
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/py2app/build_app.py", line 1214, in create_binaries
    platfiles = mm.run()
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/macholib/MachOStandalone.py", line 105, in run
    mm.run_file(fn)
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/macholib/MachOGraph.py", line 84, in run_file
    self.scan_node(m)
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/macholib/MachOGraph.py", line 110, in scan_node
    m = self.load_file(filename, caller=node)
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/macholib/MachOGraph.py", line 93, in load_file
    newname = self.locate(name, loader=caller)
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/macholib/MachOStandalone.py", line 23, in locate
    newname = super(FilteredMachOGraph, self).locate(filename, loader)
  File "/Users/bancal/anaconda/lib/python3.4/site-packages/macholib/MachOGraph.py", line 49, in locate
    loader=loader.filename)
TypeError: dyld_find() got an unexpected keyword argument 'loader'

Workaround :
vi /Users/bancal/anaconda/lib/python3.4/site-packages/macholib/dyld.py /Users/bancal/anaconda/lib/python3.4/site-packages/macholib/MachOGraph.py
--- orig/MachOGraph.py	2015-03-24 15:41:05.320297546 +0100
+++ modif/MachOGraph.py	2015-03-24 15:41:28.676297559 +0100
@@ -46,7 +46,7 @@
                 try:
                     fn = dyld_find(filename, env=self.env,
                         executable_path=self.executable_path,
-                        loader=loader.filename)
+                        loader_path=loader.filename)
                     self.trans_table[(loader.filename, filename)] = fn
                 except ValueError:
                     return None

now build goes to the end :

rm -rf build dist/
python setup_osx.py py2app
[...]
done!


2015.03.26 - SB ● Create enacdrives.app
--------------------------------------------------------------------------------

Applications throws an exception when launched :

26.03.15 11:25:08.172	enacdrives[4382]	Traceback (most recent call last):
26.03.15 11:25:08.173	enacdrives[4382]	  File "/Users/bancal/SWITCHdrive/enacdrives/client/dist/enacdrives.app/Contents/Resources/__boot__.py", line 351, in <module>
26.03.15 11:25:08.173	enacdrives[4382]	    _run()
26.03.15 11:25:08.173	enacdrives[4382]	  File "/Users/bancal/SWITCHdrive/enacdrives/client/dist/enacdrives.app/Contents/Resources/__boot__.py", line 336, in _run
26.03.15 11:25:08.173	enacdrives[4382]	    exec(compile(source, path, 'exec'), globals(), globals())
26.03.15 11:25:08.173	enacdrives[4382]	  File "/Users/bancal/SWITCHdrive/enacdrives/client/dist/enacdrives.app/Contents/Resources/enacdrives.py", line 7, in <module>
26.03.15 11:25:08.173	enacdrives[4382]	    from gui import main_GUI
26.03.15 11:25:08.173	enacdrives[4382]	  File "gui.pyc", line 9, in <module>
26.03.15 11:25:08.174	enacdrives[4382]	  File "PyQt4/QtGui.pyc", line 14, in <module>
26.03.15 11:25:08.174	enacdrives[4382]	  File "PyQt4/QtGui.pyc", line 10, in __load
26.03.15 11:25:08.175	enacdrives[4382]	ImportError: dlopen(/Users/bancal/SWITCHdrive/enacdrives/client/dist/enacdrives.app/Contents/Resources/lib/python3.4/lib-dynload/PyQt4/QtGui.so, 2): Library not loaded: @loader_path/../../../libQtGui.4.dylib
26.03.15 11:25:08.175	enacdrives[4382]	  Referenced from: /Users/bancal/SWITCHdrive/enacdrives/client/dist/enacdrives.app/Contents/Resources/lib/python3.4/lib-dynload/PyQt4/QtGui.so
26.03.15 11:25:08.175	enacdrives[4382]	  Reason: image not found


Workaround/fix :
cp /Users/bancal/anaconda/lib/libQtCore.4.dylib dist/enacdrives.app/Contents/Resources/lib/
cp /Users/bancal/anaconda/lib/libQtGui.4.dylib dist/enacdrives.app/Contents/Resources/lib/


2015.03.27 - SB ● Build on Precise (12.04)
--------------------------------------------------------------------------------

Running 14.04 compiled application raises the following error :

~~~ out
./build/exe.linux-x86_64-3.4/enacdrives: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.17' not found (required by /home/bancal/enacdrives_client/build/exe.linux-x86_64-3.4/libpython3.4m.so.1.0)
~~~

FIX : Copmile on Ubuntu 12.04 (Precise)

~~~ bash
sudo apt-get install python3-minimal python-virtualenv
virtualenv -p python3.2 venv_py3
ln -s venv_py3/bin/activate .
. activate
pip install pexpect
~~~

Install PyQt4

~~~ bash
sudo apt-get install python3-pyqt4

export PYTHONPATH=/usr/lib/python3/dist-packages
~~~

Installing with pip works

~~~ bash
sudo apt-get install python3-dev
pip install cx_Freeze
~~~


2015.04.02 - SB ● Created some unittests
--------------------------------------------------------------------------------

~~~ bash
./client/test_conf.py
~~~

~~~ out
python client/test_conf.py
.............
----------------------------------------------------------------------
Ran 13 tests in 0.003s

OK
~~~

Or globaly on all test files discovered

~~~ bash
pip install nose

nosetests -v client/
~~~

~~~ out
test_bad_option (test_conf.TestReadConfigSource) ... ok
test_bad_servername (test_conf.TestReadConfigSource) ... ok
test_bool_false (test_conf.TestReadConfigSource) ... ok
test_bool_true (test_conf.TestReadConfigSource) ... ok
test_comment (test_conf.TestReadConfigSource) ... ok
test_complete_cifs_mount_entry (test_conf.TestReadConfigSource) ... ok
test_empty (test_conf.TestReadConfigSource) ... ok
test_path (test_conf.TestReadConfigSource) ... ok
test_unknown_option (test_conf.TestReadConfigSource) ... ok
test_unknown_section (test_conf.TestReadConfigSource) ... ok
test_basic_cifs_mount (test_conf.TestValidateConfig) ... ok
test_empty (test_conf.TestValidateConfig) ... ok
test_incomplete_cifs_mount (test_conf.TestValidateConfig) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.029s

OK
~~~
