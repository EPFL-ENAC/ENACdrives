# Copy this docker description to ENACdrives project folder with :
# rsync -avH --delete --force /home/sbancal/docker/build_enacdrives_U12.04_amd64/ /home/sbancal/Projects/ENACdrives/docker/build_enacdrives_U12.04_amd64/

# Build with :
# docker build -t build_enacdrives_amd64 .

# Run interactively with :
# docker run -it -v ~/Projects/ENACdrives:/enacdrives build_enacdrives_amd64 /bin/bash

# build new release with :
# docker run -v ~/Projects/ENACdrives:/enacdrives build_enacdrives_amd64 python3 setup.py build


FROM ubuntu:16.04
MAINTAINER Samuel.Bancal@epfl.ch

ENV update_date 2020-05-12
RUN apt-get update
RUN apt-get install -y vim ncurses-dev wget build-essential ca-certificates

# Python 3.8.2 from source
RUN apt-get install -y libssl-dev libffi-dev libglib2.0-0
RUN wget https://www.python.org/ftp/python/3.8.2/Python-3.8.2.tar.xz
RUN tar -xf Python-3.8.2.tar.xz
RUN cd Python-3.8.2/; \
    ./configure --prefix=/opt/python3.8; \
    make; \
    make test; \
    make install
ENV PATH /opt/python3.8/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
RUN pip3 install --upgrade pip

RUN python3 --version
RUN pip3 install pexpect
RUN pip3 install pyqt5
RUN pip3 install distro
RUN pip3 install cx_Freeze

# Build env
WORKDIR /enacdrives/client
