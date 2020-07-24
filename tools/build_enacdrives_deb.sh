#!/usr/bin/bash

export ENACDRIVES_PROJECT=~/Projects/enacdrives
pushd ${ENACDRIVES_PROJECT}

export PACKAGE=enacdrives
export SOFT="ENACdrives"
export SOFT_VER=$(python3 tools/tell_version.py)

export PACKAGE_REV=1
while :; do
  export BUILD_DIR=${ENACDRIVES_PROJECT}/debmake/${PACKAGE}_${SOFT_VER}-${PACKAGE_REV}
  export DEB_FILENAME=${BUILD_DIR}/${PACKAGE}_${SOFT_VER}-${PACKAGE_REV}_all.deb
  if [ ! -d ${BUILD_DIR} ]; then
    break
  fi
  export PACKAGE_REV=$(echo ${PACKAGE_REV}+1 | bc)
done

echo Ready to build ${DEB_FILENAME}
read -p "Press enter to continue or Ctrl-C to abort"

mkdir ${BUILD_DIR}

if [ ! -d ${PACKAGE}-${SOFT_VER} ]; then
  ln -s client ${PACKAGE}-${SOFT_VER}
fi
tar -chvzf ${BUILD_DIR}/${PACKAGE}-${SOFT_VER}.tar.gz ${PACKAGE}-${SOFT_VER}
cd ${BUILD_DIR}
tar -xzf ${PACKAGE}-${SOFT_VER}.tar.gz
cd ${PACKAGE}-${SOFT_VER}
debmake -b':py3' -r ${PACKAGE_REV}

cat > debian/control <<EOF
Source: ${PACKAGE}
Section: misc
Priority: optional
Maintainer: Samuel Bancal <Samuel.Bancal@epfl.ch>
Build-Depends: debhelper (>=11~), dh-python, python3-all
Standards-Version: 4.1.4
Homepage: https://enacit.epfl.ch/${PACKAGE}/
X-Python3-Version: >= 3.2

Package: ${PACKAGE}
Architecture: all
Multi-Arch: foreign
Depends: libc6 (>= 2.15), cifs-utils, gvfs-bin, python3-pyqt5, ${misc:Depends}, ${python3:Depends}
Description: EPFL, ENAC and units NAS directory
 An application that let the user know which NAS he has access to and
 mount/umount them. It can be used with the graphical interface
 (Linux/Windows/MacOSX) and the command line (Linux only).
EOF

debuild

popd

echo Done preparing ${DEB_FILENAME}
