% New client ENACdrives : Workflow
% SB, ND, SN, PDJ (ENAC-IT)


COMMON
======

* Project repo : https://_username_@git.epfl.ch/repo/enacdrives.git
* Release version : set in enacdrives/client/utility.py (CONST.VERSION & CONST.FULL_VERSION & CONST.PACKAGE_SIGNATURE_VERSION)


LINUX
=====


Compile
-------

~~~ bash
docker run -v ~/Projects/enacdrives:/enacdrives build_enacdrives_amd64 python3 setup.py install --prefix=/enacdrives/client/build/debian/usr
~~~


Package
-------

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

reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb precise enacdrives.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb trusty enacdrives.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb utopic enacdrives.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb vivid enacdrives.deb
~~~


WINDOWS
=======

<SB>

~~~ bash
cp -R /home/sbancal/Projects/enacdrives/client/ /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/
rm -f /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/ENACdrives.py
cp /home/sbancal/Projects/enacdrives/client/enacdrives.py /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/
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
export PYTHONPATH=/usr/lib/python3/dist-packages
export VERSION=$(python ~/Projects/enacdrives/client/tell_version.py)

pushd ~/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/
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
python setup_osx.py py2app
cp /Users/bancal/anaconda/lib/libQtCore.4.dylib dist/ENACdrives.app/Contents/Resources/lib/
cp /Users/bancal/anaconda/lib/libQtGui.4.dylib dist/ENACdrives.app/Contents/Resources/lib/
~~~

Test ... and give it to IT3 for Packaging via http://enacshare.epfl.ch (with Safari ... so that app is sent without preparing a zip)
Sending it through CIFS share kills UNIX permissions :(
