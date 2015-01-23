% mount_filers
% enac.epfl.ch - Samuel Bancal


2015.01.19 - SB ● Python Qt5
--------------------------------------------------------------------------------

Installed System wide because couldn't find PyQt5 in pip

~~~ bash
sudo apt-get install python3-pyqt5
~~~

~~~ out
The following extra packages will be installed:
libqt5clucene5 libqt5designer5 libqt5help5 python3-sip
Suggested packages:
python3-pyqt5-dbg
The following NEW packages will be installed:
libqt5clucene5 libqt5designer5 libqt5help5 python3-pyqt5 python3-sip
0 upgraded, 5 newly installed, 0 to remove and 0 not upgraded.
Need to get 5,401 kB of archives.
After this operation, 22.2 MB of additional disk space will be used.
~~~


2015.01.19 - SB ● Virtualenv + iPython
--------------------------------------------------------------------------------

~~~ bash
cd ~/Projects/mount_filers/client
virtualenv -p python3.4 venv_py3
. venv_py3/bin/activate
pip install ipython
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
ipython==2.3.1
~~~

