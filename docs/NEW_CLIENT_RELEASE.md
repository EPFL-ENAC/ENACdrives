% New client ENACdrives : Workflow
% SB, ND, SN, PDJ (ENAC-IT)


COMMON
======

* Project repo : https://_username_@git.epfl.ch/repo/enacdrives.git
* Release version : set in enacdrives/client/utility.py (CONST.VERSION & CONST.VERSION_DATE)


LINUX
=====


Compile & Package
-----------------

~~~ bash
~/Projects/enacdrives/tools/build_enacdrives_deb.sh
~~~


Send package to enacrepo.epfl.ch
--------------------------------

~~~ bash
cd ~/Projects/enacdrives/deb_building/
sshfs enacit1@enacrepo:/data/web/enacrepo/ enacrepo.epfl.ch/

reprepro -b enacrepo.epfl.ch/public/ list precise
reprepro -b enacrepo.epfl.ch/public/ list trusty
reprepro -b enacrepo.epfl.ch/public/ list utopic
reprepro -b enacrepo.epfl.ch/public/ list vivid

reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb precise enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb precise enacdrives_amd64.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb trusty enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb trusty enacdrives_amd64.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb utopic enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb utopic enacdrives_amd64.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb vivid enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb vivid enacdrives_amd64.deb
~~~


WINDOWS
=======

<SB>

~~~ bash
enacdrives -n nas3_enac-it_files
cp -R /home/sbancal/Projects/enacdrives/client/ /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/
rm -rf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/exe.win32-3.4
~~~

~~~
cd Y:\common\ENACdrives\src\client
Y:
python setup.py build
~~~

Test ...

Make a zip (-> PortableApps)
~~~ bash
export VERSION=$(PYTHONPATH=/usr/lib/python3/dist-packages python3 ~/Projects/enacdrives/client/tell_version.py); echo $VERSION

pushd ~/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/
rm -rf ENACdrives-${VERSION} ENACdrives-${VERSION}.zip
cp -r exe.win32-3.4 ENACdrives-${VERSION}
zip -r ENACdrives-${VERSION}.zip ENACdrives-${VERSION}/
popd
~~~

Give it to IT2 for Packaging
~~~ bash
rm -rf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built
mv /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/exe.win32-3.4 /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built
rm -rf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built/enacdrives.conf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built/enacdrives.cache /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built/execution_output.txt
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
ssh -p 2210 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null bancal@localhost
cd ~/enacdrives_client/
rm -rf dist/*
mv enacdrives.py ENACdrives.py
python setup_osx.py py2app
cp /Users/bancal/anaconda/lib/libQtCore.4.dylib dist/ENACdrives.app/Contents/Resources/lib/
cp /Users/bancal/anaconda/lib/libQtGui.4.dylib dist/ENACdrives.app/Contents/Resources/lib/
~~~

Test ... and give it to IT3 for Packaging via http://enacshare.epfl.ch (with Safari ... so that app is sent without preparing a zip)
Sending it through CIFS share kills UNIX permissions :(
