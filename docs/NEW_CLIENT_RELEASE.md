% New client ENACdrives : Workflow
% SB, ND, SN, PDJ (ENAC-IT)


COMMON
======

* Project repo : https://_username_@git.epfl.ch/repo/enacdrives.git
* Release version : set in enacdrives/client/utility.py (CONST.VERSION & CONST.FULL_VERSION)


LINUX
=====


WINDOWS
=======

<SB>

~~~ bash
cp -R /home/sbancal/Projects/enacdrives/client/ /home/sbancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/src/
~~~

~~~
cd Y:\commun1\ENACdrives\src\client
python setup.py build
~~~

Test ... and give it to IT2 for Packaging

~~~ bash
rm -rf /home/sbancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/Windows/built
mv /home/sbancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/src/client/build/exe.win32-3.4 /home/sbancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/Windows/built
rm -rf /home/sbancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/Windows/built/enacdrives.conf /home/sbancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/Windows/built/enacdrives.cache
~~~

<ND>
...



MACOSX
======

~~~ bash
alias to_macp="rsync -e 'ssh -p 2210' -avH --exclude venv_py3 --exclude __pycache__  ~/Projects/enacdrives/client/ bancal@localhost:enacdrives_client/"
to_macp
~~~

~~~ bash
cd ~/enacdrives_client/
python setup_osx.py py2app
cp /Users/bancal/anaconda/lib/libQtCore.4.dylib dist/enacdrives.app/Contents/Resources/lib/
cp /Users/bancal/anaconda/lib/libQtGui.4.dylib dist/enacdrives.app/Contents/Resources/lib/
~~~

Test ... and give it to IT3 for Packaging

~~~ bash
cp -r /Users/bancal/enacdrives_client/dist/enacdrives.app /Users/bancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/MacOSX/
~~~
