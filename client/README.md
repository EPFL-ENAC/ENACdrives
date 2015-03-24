% mount_filers
% enac.epfl.ch - Samuel Bancal


2015.01.19 - SB ● Python Qt4
--------------------------------------------------------------------------------

Installed System wide because couldn't find PyQt4 in pip

~~~ bash
sudo apt-get install python3-pyqt4
~~~


2015.01.19 - SB ● Virtualenv + iPython
--------------------------------------------------------------------------------

~~~ bash
cd ~/Projects/mount_filers
virtualenv -p python3.4 venv_py3
ln -s venv_py3/bin/activate .
. activate
pip install ipython
pip install pexpect
~~~


2015.01.19 - SB ● 1st Python Qt app test
--------------------------------------------------------------------------------

~~~ bash
export PYTHONPATH=/usr/lib/python3/dist-packages
./client/test.py
~~~


2015.01.19 - SB ● cx_Freeze (compile Python to executables)
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


2015.02.02 - SB ● cx_Freeze Install on MacOSX
--------------------------------------------------------------------------------

1. Install Xcode
2. Launch Xcode to agree the licence
3. Install Anaconda3 64b from http://continuum.io/downloads#py34
4. pip install cx_Freeze
   FAILED !!!


2015.02.19 - SB ● Windows install winpexpect
--------------------------------------------------------------------------------

~~~ cmd
pip install winpexpect
~~~


2015.03.24 - SB ● MacOSX install py2app
--------------------------------------------------------------------------------

~~~ cmd
pip install py2app
~~~


2015.03.24 - SB ● MacOSX created mount_filers.icns (icon set)
--------------------------------------------------------------------------------

Instructions at http://applehelpwriter.com/2012/12/16/make-your-own-icns-icons-for-free/

create Folder "iconbuilder.iconset" (accept the extension ".iconset")
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

iconutil -c icns ~/Desktop/iconbuilder.iconset

It's done. Rename it "mount_filers.icns"!


2015.03.24 - SB ● Create mount_filers.app
--------------------------------------------------------------------------------

py2applet --make-setup mount_filers.py mount_filers.icns

This creates a setup.py ... rename it to setup_osx.py

python setup_osx.py py2app
