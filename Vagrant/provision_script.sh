#!/bin/bash

function title1 {
    string=$*
    length=$(echo ${#string} + 10 | bc)
    echo "---> $@ <---"
    printf %${length}s |tr " " "="
    echo -e "\n"
}

function title2 {
    string=$*
    length=$(echo ${#string} + 10 | bc)
    echo "---> $@ <---"
    printf %${length}s |tr " " "-"
    echo -e "\n"
}

function title3 {
    echo "### ---> $@ <---"
    echo
}


title1 "Start provisioning"
export DEBIAN_FRONTEND=noninteractive
. /vagrant/secrets.sh

title2 "Setup keyboard..."
sed -i.bak 's/^XKBMODEL=.*/XKBMODEL="pc105"/' /etc/default/keyboard
sed -i.bak 's/^XKBLAYOUT=.*/XKBLAYOUT="ch"/' /etc/default/keyboard
sed -i.bak 's/^XKBVARIANT=.*/XKBVARIANT="fr"/' /etc/default/keyboard
sed -i.bak 's/^XKBOPTIONS=.*/XKBOPTIONS=""/' /etc/default/keyboard
setupcon --force

title2 "User sbancal"
sudo groupadd sbancal
sudo useradd -m -c "Bancal Samuel" -g sbancal -G adm,dialout,cdrom,floppy,sudo,audio,dip,video,plugdev,netdev -s /bin/bash sbancal
usermod --password ${SBANCAL_SHADOW} sbancal

title2 "SSH authorized keys"
mkdir -p /home/sbancal/.ssh
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAu6bEzrBrGzoxdbgaAFhd2fPy6zhanEOMrS9TnOK9tct2HvvxCFNcEbc5XAl9mwXdDKU22BqOJHVCgSL7iURALSVVm76jeJO1bK5NAY+37KvtNwl3BwTebeKUdwr0Rq3QCVSbryuge3KOY+EtfSRweCbTe5llE1qu2kra+7FUgd00IC/uqsp9j8P7bzfOEFDDdHuNgXhNPB/B1fZs8lfdbaUa7oGZhoyG4A7tvfRxq4DaLnWL7C60Kqkay37E8p2GV5QayAH4BaHS8/3atT55UxzrTxlIcno3+Ge4XXxvDIuMqBHLmKFjapG0oMyWjnInton0e239QMhI6bYmseoMjw== Samuel.Bancal@epfl.ch' >> /home/sbancal/.ssh/authorized_keys

title2 "Setup to use mirror.switch.ch"
sed -i -e "s/http:\\/\\/archive.ubuntu.com/http:\\/\\/mirror.switch.ch\\/ftp\\/mirror\\/ubuntu/g" /etc/apt/sources.list

title2 "update and dist-upgrade"
apt-get -q -y update
apt-get -q -y dist-upgrade

title2 "purge chef and puppet"
apt-get -q -y purge chef chef-zero puppet puppet-common

# Python env
title2 "Install Server basics"
apt-get -q -y install vim tree meld multitail ipython
apt-get -q -y install build-essential python-dev python-pip

title2 "Install Mail"
apt-get -q -y install mailutils ssmtp
install -b -o root -g root -m 644 /vagrant/etc/ssmtp/ssmtp.conf /etc/ssmtp
install -b -o root -g root -m 644 /vagrant/etc/ssmtp/revaliases /etc/ssmtp

title2 "Install NTP"
apt-get -q -y install ntp
install -b -o root -g root -m 644 /vagrant/etc/ntp.conf /etc
/etc/init.d/ntp restart

title2 "Setup UFW"
ufw disable
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow proto tcp from 10.0.2.0/24 to any port 22
ufw allow proto tcp from 128.178.7.66 to any port 22
ufw allow proto tcp from any to any port 80
ufw --force enable
ufw status

title2 "Install Apache2"
apt-get -q -y install apache2 apache2-dev apache2-threaded-dev
install -b -o root -g root -m 644 /vagrant/etc/apache2/conf-available/servername.conf /etc/apache2/conf-available
a2enconf servername
service apache2 restart

title2 "Install MySQL"
apt-get -q -y install mysql-server mysql-client
install -b -o root -g root -m 644 /vagrant/etc/mysql/conf.d/enacit.cnf /etc/mysql/conf.d/
service mysql restart
mysql -u root <<EOF
create user 'enacdrives'@'localhost' identified by '${MYSQL_ENACDRIVES_PWD}';
create database enacdrives;
grant all privileges on enacdrives.* to 'enacdrives'@'localhost';
commit;
EOF
mysqladmin -u root password ${MYSQL_ROOT_PWD}

title2 "Install Tequila"
wget http://tequila.epfl.ch/download/2.0/tequila-apache-C-2.0.16.tgz
tar -xvzf tequila-apache-C-2.0.16.tgz
pushd tequila-2.0.16/Apache/C/
ed - Makefile <<EOFMakefile
g/httpd /s:httpd :apache2 :
g/apxs/s:apxs :apxs2 :
wq
EOFMakefile
make
make install
popd

title2 "Setup Tequila"
install -b -o root -g root -m 644 /vagrant/etc/apache2/mods-available/tequila.load /etc/apache2/mods-available
install -b -o root -g root -m 644 /vagrant/etc/apache2/mods-available/tequila.conf /etc/apache2/mods-available
mkdir -p /var/tequila
chown www-data: /var/tequila
a2enmod tequila
service apache2 restart
apache2ctl -t -D DUMP_MODULES | grep tequila

title2 "Install Django"
mkdir -p /django_app
chown sbancal\: /django_app
apt-get -q -y install python-virtualenv python-pip python3-dev
apt-get -q -y install libldap2-dev libsasl2-dev
apt-get -q -y install libapache2-mod-xsendfile
cat <<EOF
... Now Deploy from salsa.epfl.ch
~~~ bash
cd /home/sbancal/Projects/enacdrives/web_app
# pww
/home/sbancal/py/2/bin/fab -H enacit1sbtest4 full_deploy
~~~

Check :
<http://enacit1sbtest4.epfl.ch/config/admin>
<http://enacit1sbtest4.epfl.ch/config/config>
EOF


title2 "Clean up"
apt-get -q -y autoremove
apt-get -q -y clean
apt-get -q -y autoclean

title1 "Finished !"
