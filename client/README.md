% mount_filers
% enac.epfl.ch - Samuel Bancal


2015.01.19 - SB ● Python Qt5
--------------------------------------------------------------------------------

Installed System wide because couldn't find PyQt5 in pip

~~~ bash
sudo apt-get install python3-pyqt4
~~~


2015.01.19 - SB ● Virtualenv + iPython
--------------------------------------------------------------------------------

~~~ bash
cd ~/Projects/mount_filers/client
virtualenv -p python3.4 venv_py3
. venv_py3/bin/activate
#pip install ipython
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
