# Copy this docker description to ENACdrives project folder with :
# rsync -avH --delete --force /home/sbancal/docker/build_enacdrives_U12.04_i386/ /home/sbancal/Projects/enacdrives/docker/build_enacdrives_U12.04_i386/

# Build with :
# docker build -t build_enacdrives_i386 .

# Run interactively with :
# docker run -it -v ~/Projects/enacdrives:/enacdrives build_enacdrives_i386 /bin/bash

# build new release with :
# docker run -v ~/Projects/enacdrives:/enacdrives build_enacdrives_i386 python3 setup.py build


FROM ubuntu:12.04
MAINTAINER Samuel.Bancal@epfl.ch

ENV update_date 2015-06-25
RUN apt-get update
RUN apt-get install -y ncurses-dev wget ca-certificates vim less
RUN apt-get install -y gcc:i386 g++:i386 binutils:i386; apt-get install -y gcc:i386 g++:i386 binutils:i386
RUN apt-get install -y ia32-libs
RUN apt-get install -y make:i386
ENV OPT=-m32
ENV LDFLAGS=-m32
# apt-get install libc6-dev:i386

# Python 3.4.3 from source
RUN apt-get install -y libssl-dev:i386
RUN wget http://www.python.org/ftp/python/3.4.3/Python-3.4.3.tar.xz
RUN tar -xf Python-3.4.3.tar.xz
RUN cd Python-3.4.3/; ./configure --prefix=/opt/python3.4; make; make test; make install
ENV PATH /opt/python3.4/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN pip3 install --upgrade pip
ADD platform.py /opt/python3.4/lib/python3.4/platform.py

# cx_Freeze
RUN wget https://pypi.python.org/packages/source/c/cx_Freeze/cx_Freeze-4.3.4.tar.gz#md5=5bd662af9aa36e5432e9144da51c6378
RUN tar -xf cx_Freeze-4.3.4.tar.gz
# Patched version 2015-06-18 with Dominique Quatravaux
ADD setup.py cx_Freeze-4.3.4/setup.py
RUN cd cx_Freeze-4.3.4/; python3.4 setup.py install

# SIP (dependency for PyQt4)
RUN wget http://sourceforge.net/projects/pyqt/files/sip/sip-4.16.8/sip-4.16.8.tar.gz
RUN tar -xf sip-4.16.8.tar.gz
RUN cd sip-4.16.8; python3 configure.py; make; make install

# PyQt4
RUN apt-get install -y qt4-qmake:i386 qt4-dev-tools:i386
# RUN apt-get install -y python-pip python2.7-dev libxext-dev python-qt4 qt4-dev-tools build-essential
RUN wget http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.4/PyQt-x11-gpl-4.11.4.tar.gz
RUN tar -xf PyQt-x11-gpl-4.11.4.tar.gz
RUN cd PyQt-x11-gpl-4.11.4; python3 configure.py --confirm-license; make; make install

# pexpect
RUN pip install pexpect

# Build env
WORKDIR /enacdrives/client
