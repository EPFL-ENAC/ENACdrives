% New client ENACdrives : Workflow
% SB, ND, SN, PDJ (ENAC-IT)


COMMON
======

* Project repo : https://_username_@git.epfl.ch/repo/enacdrives.git
* Release version : set in enacdrives/client/utility.py (CONST.VERSION & CONST.FULL_VERSION & CONST.PACKAGE_SIGNATURE_VERSION)


LINUX
=====

~~~ bash
# On salsa.epfl.ch
alias to_pp="rsync -e 'ssh -p 2220' -avH --exclude venv_py3 --exclude __pycache__  ~/Projects/enacdrives/client/ bancal@localhost:enacdrives_client/"
to_pp
~~~

~~~ bash
# On precise-vm
cd ~/enacdrives_client/
. ./activate 
export PYTHONPATH=/usr/lib/python3/dist-packages
python setup.py build
~~~

~~~ bash
# On salsa.epfl.ch
alias from_pp="rsync -e 'ssh -p 2220' -avH --exclude venv_py3 --exclude __pycache__ bancal@localhost:enacdrives_client/build/exe.linux-x86_64-3.2/ ~/Projects/enacdrives/client/build/exe.linux-x86_64-3.2/"
from_pp
~~~

Build a package - Definition
----------------------------

~~~ bash
cd ~/Projects/enacdrives/client
. ../activate 
export PACKAGE=enacdrives
export SOFT="ENACdrives"
export SHORT_SOFT_VER=$(python tell_version.py)
export SOFT_VER=$(python tell_version.py)
export PACKAGE_VER=1
export DIR_DEB_CREATION=~/Projects/enacdrives/deb_building/${PACKAGE}
echo "${SOFT} ${SOFT_VER} -> ${DIR_DEB_CREATION}"
~~~

Build a package - Cleanup
-------------------------

~~~ bash
sudo rm -rf ${DIR_DEB_CREATION}
mkdir -p ${DIR_DEB_CREATION}
~~~


Build a package - Content
-------------------------

~~~ bash
mkdir -p ${DIR_DEB_CREATION}/opt/enacdrives
cp -r ~/Projects/enacdrives/client/build/exe.linux-x86_64-3.2/* ${DIR_DEB_CREATION}/opt/enacdrives/
mkdir -p ${DIR_DEB_CREATION}/usr/local/bin
ln -s /opt/enacdrives/enacdrives ${DIR_DEB_CREATION}/usr/local/bin
mkdir -p ${DIR_DEB_CREATION}/etc
cat > ${DIR_DEB_CREATION}/etc/enacdrives.conf << %%%EOF%%%
# Full documentation here : http://enacit.epfl.ch/enacdrives/
%%%EOF%%%
~~~


Build a package - Meta informations
-----------------------------------

~~~ bash
mkdir -p ${DIR_DEB_CREATION}/DEBIAN
cat > ${DIR_DEB_CREATION}/DEBIAN/control << %%%EOF%%%
Package: ${PACKAGE}
Version: ${SOFT_VER}-${PACKAGE_VER}
Architecture: all
Depends: gvfs-bin
Recommends: cifs-utils
Homepage: http://enacit.epfl.ch/enacdrives
Maintainer: Samuel BANCAL <Samuel.Bancal@epfl.ch>
Section: main
Priority: extra
Description: Tool to access every user storage with centralized configuration.
%%%EOF%%%


# creation of the DEBIAN/postrm (post-remove)
cat > ${DIR_DEB_CREATION}/DEBIAN/postrm << %%%EOF%%%
#!/bin/bash

%%%EOF%%%
chmod 755 ${DIR_DEB_CREATION}/DEBIAN/postrm


# creation of the DEBIAN/conffiles
# used to manage which file is a config file and should not be overwriten
# by new versions by default.
cat > ${DIR_DEB_CREATION}/DEBIAN/conffiles << %%%EOF%%%
/etc/enacdrives.conf
%%%EOF%%%


# Icon and a Launcher
mkdir -p ${DIR_DEB_CREATION}/usr/share/pixmaps/
cp ~/Projects/enacdrives/graphics/enacdrives.svg ${DIR_DEB_CREATION}/usr/share/pixmaps/
mkdir -p ${DIR_DEB_CREATION}/usr/share/applications
cat > ${DIR_DEB_CREATION}/usr/share/applications/enacdrives.desktop << %%%EOF%%%
[Desktop Entry]
Version=${SOFT_VER}
Name=${SOFT}
Comment=Mount any of your EPFL NAS filers
Exec=/opt/enacdrives/enacdrives
Icon=/usr/share/pixmaps/enacdrives.svg
Terminal=false
Type=Application
Categories=GNOME;GTK;System;
%%%EOF%%%

sudo chown -R root: ${DIR_DEB_CREATION}
~~~


Build a package - The .deb
--------------------------

~~~ bash
find ${DIR_DEB_CREATION} -name '*~'
find ${DIR_DEB_CREATION} -name '*~' -exec rm {} \;

cd ~/Projects/enacdrives/deb_building/
fakeroot dpkg -b ${PACKAGE}

cp ${PACKAGE}.deb ${PACKAGE}-${SHORT_SOFT_VER}-${PACKAGE_VER}.deb
~~~


Send package to enacrepo.epfl.ch
--------------------------------

~~~ bash
cd ~/Projects/enacdrives/deb_building/
sshfs enacit1@enacrepo:/data/web/enacrepo/ enacrepo.epfl.ch/

reprepro -b enacrepo.epfl.ch/public/ list trusty
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb trusty enacdrives.deb
~~~


WINDOWS
=======

<SB>

~~~ bash
cp -R /home/sbancal/Projects/enacdrives/client/ /home/sbancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/src/
~~~

~~~
cd Y:\commun1\ENACdrives\src\client
Y:
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
rm -rf /Users/bancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/MacOSX/enacdrives.app
cp -r /Users/bancal/enacdrives_client/dist/enacdrives.app /Users/bancal/Desktop/enac-it_on_enacfiles1/commun1/ENACdrives/MacOSX/
~~~
