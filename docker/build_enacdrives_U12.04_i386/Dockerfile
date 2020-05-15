# Copy this docker description to ENACdrives project folder with :
# rsync -avH --delete --force /home/sbancal/docker/build_enacdrives_U12.04_i386/ /home/sbancal/Projects/enacdrives/docker/build_enacdrives_U12.04_i386/

# Build with :
# docker build -t build_enacdrives_i386 .

# Run interactively with :
# docker run -it -v ~/Projects/enacdrives:/enacdrives build_enacdrives_i386 /bin/bash

# build new release with :
# docker run -v ~/Projects/enacdrives:/enacdrives build_enacdrives_i386 python3 setup.py build


FROM ubuntu:16.04
MAINTAINER Samuel.Bancal@epfl.ch

ENV update_date 2020-05-12
RUN apt-get update
# RUN apt-get install -y ncurses-dev wget ca-certificates vim less
# RUN apt-get install -y gcc:i386 g++:i386 binutils:i386; apt-get install -y gcc:i386 g++:i386 binutils:i386
# RUN apt-get install -y ia32-libs
# RUN apt-get install -y make:i386
# ENV OPT=-m32
# ENV LDFLAGS=-m32
# # apt-get install libc6-dev:i386
# 
# # Python 3.8.2 from source
# RUN apt-get install -y libssl-dev:i386
# RUN wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tar.xz
# RUN tar -xf Python-3.8.2.tar.xz
# RUN cd Python-3.8.2/; ./configure --prefix=/opt/python3.8; make; make test; make install
# ENV PATH /opt/python3.8/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
# RUN pip3 install --upgrade pip
# 
# RUN python3 --version
# RUN pip3 install pexpect
# RUN pip3 install pyqt5
# RUN pip3 install distro
# 
# # Build env
# WORKDIR /enacdrives/client
