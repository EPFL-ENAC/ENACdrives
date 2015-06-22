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

mkdir -m 755 ${DIR_DEB_CREATION}/opt
mkdir -m 755 ${DIR_DEB_CREATION}/opt/enacdrives
cp -r ~/Projects/enacdrives/client/build/exe.linux-x86_64-3.4/* ${DIR_DEB_CREATION}/opt/enacdrives/
chmod 644 ${DIR_DEB_CREATION}/opt/enacdrives/*.png
chmod 644 ${DIR_DEB_CREATION}/opt/enacdrives/*.ico
mkdir -m 755 ${DIR_DEB_CREATION}/usr
mkdir -m 755 ${DIR_DEB_CREATION}/usr/local
mkdir -m 755 ${DIR_DEB_CREATION}/usr/local/bin
ln -s /opt/enacdrives/enacdrives ${DIR_DEB_CREATION}/usr/local/bin
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
Exec=/opt/enacdrives/enacdrives
Icon=/usr/share/pixmaps/enacdrives.svg
Terminal=false
Type=Application
Categories=GNOME;GTK;System;
%%%EOF%%%
chmod 644 ${DIR_DEB_CREATION}/usr/share/applications/enacdrives.desktop


ESTIMATE_INSTALLED_SIZE=0
ESTIMATE_INSTALLED_SIZE=$(echo ${ESTIMATE_INSTALLED_SIZE} + $(du -sk ${DIR_DEB_CREATION}/etc/ | awk '{ print $1 }') | bc)
ESTIMATE_INSTALLED_SIZE=$(echo ${ESTIMATE_INSTALLED_SIZE} + $(du -sk ${DIR_DEB_CREATION}/usr/ | awk '{ print $1 }') | bc)
ESTIMATE_INSTALLED_SIZE=$(echo ${ESTIMATE_INSTALLED_SIZE} + $(du -sk ${DIR_DEB_CREATION}/opt/ | awk '{ print $1 }') | bc)


# Build a package - Meta informations
# -----------------------------------

mkdir -p ${DIR_DEB_CREATION}/DEBIAN
cat > ${DIR_DEB_CREATION}/DEBIAN/control << %%%EOF%%%
Package: ${PACKAGE}
Version: ${SOFT_VER}-${PACKAGE_VER}
Installed-Size: ${ESTIMATE_INSTALLED_SIZE}
Architecture: amd64
Depends: gvfs-bin
Recommends: cifs-utils
Homepage: http://enacit.epfl.ch/enacdrives
Maintainer: Samuel BANCAL <Samuel.Bancal@epfl.ch>
Section: main
Priority: extra
Description: Application to automate access to EPFL, ENAC and units NAS
%%%EOF%%%
chmod 644 ${DIR_DEB_CREATION}/DEBIAN/control

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
chmod 644 ${DIR_DEB_CREATION}/DEBIAN/conffiles


# Build a package - The .deb
# --------------------------

sudo chown -R root: ${DIR_DEB_CREATION}
find ${DIR_DEB_CREATION} -name '*~'
find ${DIR_DEB_CREATION} -name '*~' -exec rm {} \;

tree -a ${DIR_DEB_CREATION} 

cd ~/Projects/enacdrives/deb_building/
fakeroot dpkg -b ${PACKAGE}

cp ${PACKAGE}.deb ${PACKAGE}-${SHORT_SOFT_VER}-${PACKAGE_VER}.deb

popd
