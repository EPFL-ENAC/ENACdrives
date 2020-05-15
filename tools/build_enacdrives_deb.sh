#!/bin/bash

# Bancal Samuel
# 2015-06-18
# Builds the current ENACdrives package

# Pre-requisite :
# sudo apt-get install chrpath
if ! which chrpath > /dev/null; then
  echo "Please install chrpath"
  exit 1
fi

# Build a package - Definition
# ----------------------------

export ENACDRIVES_PROJECT=~/Projects/enacdrives

pushd ${ENACDRIVES_PROJECT}/client
export PYTHONPATH=/usr/lib/python3/dist-packages
export PACKAGE=enacdrives
export SOFT="ENACdrives"
export SHORT_SOFT_VER=$(pipenv run python tell_version.py)
export SOFT_VER=$(pipenv run python tell_version.py)
export PACKAGE_VER=1

# Build a package - Content
# -------------------------

build_deb (){
    # arch = amd64 | i386
    arch=${1-amd64}

    # Working folder
    export DIR_DEB_CREATION=${ENACDRIVES_PROJECT}/deb_building/${PACKAGE}_${arch}
    echo
    echo "Now Building ${PACKAGE}_${SHORT_SOFT_VER}-${PACKAGE_VER}_${arch}.deb in ${DIR_DEB_CREATION}"
    echo "------------"
    echo

    # Cleanup
    sudo rm -rf ${DIR_DEB_CREATION}
    mkdir -p ${DIR_DEB_CREATION}

    # Content - Compile
    docker run -v ${ENACDRIVES_PROJECT}:/enacdrives build_enacdrives_${arch} python3 setup.py install --prefix=/enacdrives/deb_building/${PACKAGE}_${arch}/usr
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
    cp ${ENACDRIVES_PROJECT}/graphics/enacdrives.svg ${DIR_DEB_CREATION}/usr/share/pixmaps/

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

    # Content - /usr/share/doc/enacdrives/copyright
    mkdir -p -m 755 ${DIR_DEB_CREATION}/usr/share/doc/${PACKAGE}
    cat ${ENACDRIVES_PROJECT}/client/usr_share_doc_enacdrives/copyright | sed "s/{DATETIME}/$(date)/g" > ${DIR_DEB_CREATION}/usr/share/doc/${PACKAGE}/copyright
    chmod 644 ${DIR_DEB_CREATION}/usr/share/doc/${PACKAGE}/copyright

    gzip -9 ${ENACDRIVES_PROJECT}/client/usr_share_doc_enacdrives/changelog.Debian \
      -c > ${DIR_DEB_CREATION}/usr/share/doc/${PACKAGE}/changelog.Debian.gz
    chmod 644 ${DIR_DEB_CREATION}/usr/share/doc/${PACKAGE}/changelog.Debian.gz

    # FIX unstripped-binary-or-object
    # https://lintian.debian.org/tags/unstripped-binary-or-object.html
    # https://github.com/vbatts/SlackBuilds/blob/master/cx_Freeze/cx_Freeze.SlackBuild
    find ${DIR_DEB_CREATION} -print0 | xargs -0 file | grep -e "executable" -e "shared object" | grep ELF | cut -f 1 -d : | xargs strip --strip-unneeded 2> /dev/null || true

    # # FIX binary-or-shlib-defines-rpath on
    # # + usr/lib/ENACdrives-1.2.0/lib/PyQt5/Qt/lib/libicudata.so.56 /home/qt/icu_install/lib
    # # + usr/lib/ENACdrives-1.2.0/lib/PyQt5/Qt/lib/libicui18n.so.56 /home/qt/icu_install/lib
    # # + usr/lib/ENACdrives-1.2.0/lib/PyQt5/Qt/lib/libicuuc.so.56 /home/qt/icu_install/lib
    # # https://lintian.debian.org/tags/binary-or-shlib-defines-rpath.html
    # # http://linux.die.net/man/1/chrpath
    find ${DIR_DEB_CREATION} -name libicudata.so.56 \
      -o -name libicui18n.so.56 -o -name libicuuc.so.56 | xargs chrpath -d

    # # FIX package-installs-python-bytecode
    # # https://lintian.debian.org/tags/package-installs-python-bytecode.html
    # find ${DIR_DEB_CREATION} -name '*.pyc' -exec rm -f \{\} \;

    # FIX shlib-with-executable-bit
    # https://lintian.debian.org/tags/shlib-with-executable-bit.html
    find ${DIR_DEB_CREATION}/usr/lib -type f -perm /+x -exec chmod 0644 \{\} \;
    chmod 755 ${DIR_DEB_CREATION}/usr/lib/${SOFT}-${SOFT_VER}/enacdrives

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
Depends: libc6 (>= 2.15), cifs-utils, gvfs-bin
Replaces: mountfilers
Section: misc
Priority: optional
Homepage: http://enacit.epfl.ch/enacdrives
Description: EPFL, ENAC and units NAS directory
 An application that let the user know which NAS he has access to and
 mount/umount them. It can be used with the graphical interface
 (Linux/Windows/MacOSX) and the command line (Linux only).
%%%EOF%%%
    chmod 644 ${DIR_DEB_CREATION}/DEBIAN/control

    # Meta - DEBIAN/md5sums
    cd ${DIR_DEB_CREATION}
    find etc usr -type f -exec md5sum \{\} >> DEBIAN/md5sums \;
    chmod 644 ${DIR_DEB_CREATION}/DEBIAN/md5sums

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

lint (){
  # arch = amd64 | i386
  arch=${1-amd64}

  echo
  echo lintian ${PACKAGE}_${arch}.deb
  lintian ${PACKAGE}_${arch}.deb
}


# Edit changelog.Debian and copyright
vi ${ENACDRIVES_PROJECT}/client/usr_share_doc_enacdrives/changelog.Debian
vi ${ENACDRIVES_PROJECT}/client/usr_share_doc_enacdrives/copyright

# Prepare Docker containers
docker build -t build_enacdrives_amd64 ../docker/build_enacdrives_U12.04_amd64

# Cleanup
sudo rm -rf ${ENACDRIVES_PROJECT}/client/build

# Build
build_deb amd64

# Lint
lint amd64

popd
