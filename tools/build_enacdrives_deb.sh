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

# Build a package - Content
# -------------------------

build_deb (){
    # arch = amd64 | i386
    arch=${1-amd64}

    # Working folder
    export DIR_DEB_CREATION=~/Projects/enacdrives/deb_building/${PACKAGE}_${arch}
    echo
    echo "Now Building ${PACKAGE}_${SHORT_SOFT_VER}-${PACKAGE_VER}_${arch}.deb in ${DIR_DEB_CREATION}"
    echo "------------"
    echo
    
    # Cleanup
    sudo rm -rf ${DIR_DEB_CREATION}
    mkdir -p ${DIR_DEB_CREATION}
    
    # Content - Compile
    docker run -v ~/Projects/enacdrives:/enacdrives build_enacdrives_${arch} python3 setup.py install --prefix=/enacdrives/deb_building/${PACKAGE}_${arch}/usr
    sudo chown -R sbancal\: ${DIR_DEB_CREATION}

    # Content - permissions
    find ${DIR_DEB_CREATION} -name '*.png' -exec chmod 644 \{\} \;
    find ${DIR_DEB_CREATION} -name '*.ico' -exec chmod 644 \{\} \;

    # Content - /etc/enacdrives.conf
    mkdir -m 755 ${DIR_DEB_CREATION}/etc
    cat > ${DIR_DEB_CREATION}/etc/enacdrives.conf << %%%EOF%%%
# Full documentation here : http://enacit.epfl.ch/enacdrives/
%%%EOF%%%
    chmod 644 ${DIR_DEB_CREATION}/etc/enacdrives.conf

    # Content - /usr/share/pixmaps/enacdrives.svg
    mkdir -m 755 ${DIR_DEB_CREATION}/usr/share/
    mkdir -m 755 ${DIR_DEB_CREATION}/usr/share/pixmaps/
    cp ~/Projects/enacdrives/graphics/enacdrives.svg ${DIR_DEB_CREATION}/usr/share/pixmaps/
    
    # Content - /usr/share/applications/enacdrives.desktop
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

    # Content - size
    ESTIMATE_INSTALLED_SIZE=0
    ESTIMATE_INSTALLED_SIZE=$(echo ${ESTIMATE_INSTALLED_SIZE} + $(du -sk ${DIR_DEB_CREATION}/etc/ | awk '{ print $1 }') | bc)
    ESTIMATE_INSTALLED_SIZE=$(echo ${ESTIMATE_INSTALLED_SIZE} + $(du -sk ${DIR_DEB_CREATION}/usr/ | awk '{ print $1 }') | bc)

    # Meta
    mkdir -m 755 ${DIR_DEB_CREATION}/DEBIAN
    # Meta - DEBIAN/control
    cat > ${DIR_DEB_CREATION}/DEBIAN/control << %%%EOF%%%
Package: ${PACKAGE}
Source: ${PACKAGE}
Version: ${SOFT_VER}-${PACKAGE_VER}
Architecture: ${arch}
Maintainer: Samuel Bancal <Samuel.Bancal@epfl.ch>
Installed-Size: ${ESTIMATE_INSTALLED_SIZE}
Depends: gvfs-bin
Recommends: cifs-utils
Replaces: mountfilers
Section: misc
Priority: optional
Homepage: http://enacit.epfl.ch/enacdrives
Description: EPFL, ENAC and units NAS directory
 An application that let the user know which NAS he has access to and
 mount/umount them. It can be used with :
 + the graphical interface (Linux/Windows/MacOSX)
 + a command line (Linux only).
%%%EOF%%%
    chmod 644 ${DIR_DEB_CREATION}/DEBIAN/control
    
    # Meta - DEBIAN/md5sums
    cd ${DIR_DEB_CREATION}
    find etc usr -type f -exec md5sum \{\} >> DEBIAN/md5sums \;

    # Meta - DEBIAN/conffiles
    cat > ${DIR_DEB_CREATION}/DEBIAN/conffiles << %%%EOF%%%
/etc/enacdrives.conf
%%%EOF%%%
    chmod 644 ${DIR_DEB_CREATION}/DEBIAN/conffiles

    # Package
    sudo chown -R root: ${DIR_DEB_CREATION}
    tree -a ${DIR_DEB_CREATION} 

    cd ${DIR_DEB_CREATION}/..

    fakeroot dpkg -b ${PACKAGE}_${arch}
    cp ${PACKAGE}_${arch}.deb ${PACKAGE}_${SHORT_SOFT_VER}-${PACKAGE_VER}_${arch}.deb
}

# Build
build_deb i386
build_deb amd64

# Lint
echo
echo lintian ${PACKAGE}_i386.deb
lintian ${PACKAGE}_i386.deb

echo
echo lintian ${PACKAGE}_amd64.deb
lintian ${PACKAGE}_amd64.deb

popd
