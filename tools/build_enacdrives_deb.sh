#!/bin/bash

# Bancal Samuel
# 2015-06-18
# Builds the current ENACdrives package


# Build a package - Definition
# ----------------------------

pushd ~/Projects/enacdrives/client
. ../activate
export PYTHONPATH=/usr/lib/python3/dist-packages
export PACKAGE=enacdrives
export SOFT="ENACdrives"
export SHORT_SOFT_VER=$(python tell_version.py)
export SOFT_VER=$(python tell_version.py)
export PACKAGE_VER=1
export DIR_DEB_CREATION=~/Projects/enacdrives/deb_building/${PACKAGE}
echo "${SOFT} ${SOFT_VER}-${PACKAGE_VER} -> ${DIR_DEB_CREATION}"


# Build a package - Cleanup
# -------------------------

sudo rm -rf ${DIR_DEB_CREATION}
mkdir -p ${DIR_DEB_CREATION}


# Build a package - Content
# -------------------------

docker run -v ~/Projects/enacdrives:/enacdrives build_enacdrives_amd64 python3 setup.py install --prefix=/enacdrives/deb_building/${PACKAGE}/usr
sudo chown -R sbancal\: ${DIR_DEB_CREATION}

# System wide conf file
mkdir -m 755 ${DIR_DEB_CREATION}/etc
cat > ${DIR_DEB_CREATION}/etc/enacdrives.conf << %%%EOF%%%
# Full documentation here : http://enacit.epfl.ch/enacdrives/
%%%EOF%%%
chmod 644 ${DIR_DEB_CREATION}/etc/enacdrives.conf

# Icon and a Launcher
mkdir -m 755 ${DIR_DEB_CREATION}/usr/share/
mkdir -m 755 ${DIR_DEB_CREATION}/usr/share/pixmaps/
cp ~/Projects/enacdrives/graphics/enacdrives.svg ${DIR_DEB_CREATION}/usr/share/pixmaps/
mkdir -m 755 ${DIR_DEB_CREATION}/usr/share/applications
cat > ${DIR_DEB_CREATION}/usr/share/applications/enacdrives.desktop << %%%EOF%%%
[Desktop Entry]
Version=${SOFT_VER}
Name=${SOFT}
Comment=Application to automate access to EPFL, ENAC and units NAS
Keywords=EPFL;ENAC;NAS;filers;Drives;mount;CIFS;SMB
Exec=/usr/bin/enacdrives
Icon=/usr/share/pixmaps/enacdrives.svg
Terminal=false
Type=Application
Categories=GNOME;GTK;System;
%%%EOF%%%
chmod 644 ${DIR_DEB_CREATION}/usr/share/applications/enacdrives.desktop


ESTIMATE_INSTALLED_SIZE=0
ESTIMATE_INSTALLED_SIZE=$(echo ${ESTIMATE_INSTALLED_SIZE} + $(du -sk ${DIR_DEB_CREATION}/etc/ | awk '{ print $1 }') | bc)
ESTIMATE_INSTALLED_SIZE=$(echo ${ESTIMATE_INSTALLED_SIZE} + $(du -sk ${DIR_DEB_CREATION}/usr/ | awk '{ print $1 }') | bc)


# Build a package - Meta informations
# -----------------------------------

cd ${DIR_DEB_CREATION}/..

mkdir -m 755 ${DIR_DEB_CREATION}/DEBIAN

# debian/control
cat > ${DIR_DEB_CREATION}/DEBIAN/control << %%%EOF%%%
Package: ${PACKAGE}
Source: ${PACKAGE}
Maintainer: Samuel Bancal <Samuel.Bancal@epfl.ch>
Homepage: http://enacit.epfl.ch/enacdrives
Description: Application to automate access to EPFL, ENAC and units NAS.
Version: ${SOFT_VER}-${PACKAGE_VER}
Section: misc
Priority: optional
Architecture: amd64
Installed-Size: ${ESTIMATE_INSTALLED_SIZE}
Depends: gvfs-bin
Recommends: cifs-utils
%%%EOF%%%
chmod 644 ${DIR_DEB_CREATION}/DEBIAN/control

# debian/conffiles
cat > ${DIR_DEB_CREATION}/DEBIAN/conffiles << %%%EOF%%%
/etc/enacdrives.conf
%%%EOF%%%
chmod 644 ${DIR_DEB_CREATION}/DEBIAN/conffiles

find ${DIR_DEB_CREATION} -name '*.png' -exec chmod 644 \{\} \;

sudo chown -R root: ${DIR_DEB_CREATION}
tree -a ${DIR_DEB_CREATION} 

fakeroot dpkg -b ${PACKAGE}
lintian ${PACKAGE}.deb
cp ${PACKAGE}.deb ${PACKAGE}-${SHORT_SOFT_VER}-${PACKAGE_VER}.deb

popd
