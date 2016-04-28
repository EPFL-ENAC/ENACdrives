#!/bin/bash

function title1 {
    string=$*
    length=${#string}
    echo "$@"
    printf %${length}s |tr " " "="
    echo -e "\n"
}

function title2 {
    string=$*
    length=${#string}
    echo "$@"
    printf %${length}s |tr " " "-"
    echo -e "\n"
}

function title3 {
    echo "### $@"
    echo
}


title1 "Start provisioning"

title2 "Setup keyboard..."
sed -i.bak 's/^XKBMODEL=.*/XKBMODEL="pc105"/' /etc/default/keyboard
sed -i.bak 's/^XKBLAYOUT=.*/XKBLAYOUT="ch"/' /etc/default/keyboard
sed -i.bak 's/^XKBVARIANT=.*/XKBVARIANT="fr"/' /etc/default/keyboard
sed -i.bak 's/^XKBOPTIONS=.*/XKBOPTIONS=""/' /etc/default/keyboard
setupcon --force

title2 "SSH authorized keys"
mkdir -p /root/.ssh
echo 'ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEAu6bEzrBrGzoxdbgaAFhd2fPy6zhanEOMrS9TnOK9tct2HvvxCFNcEbc5XAl9mwXdDKU22BqOJHVCgSL7iURALSVVm76jeJO1bK5NAY+37KvtNwl3BwTebeKUdwr0Rq3QCVSbryuge3KOY+EtfSRweCbTe5llE1qu2kra+7FUgd00IC/uqsp9j8P7bzfOEFDDdHuNgXhNPB/B1fZs8lfdbaUa7oGZhoyG4A7tvfRxq4DaLnWL7C60Kqkay37E8p2GV5QayAH4BaHS8/3atT55UxzrTxlIcno3+Ge4XXxvDIuMqBHLmKFjapG0oMyWjnInton0e239QMhI6bYmseoMjw== Samuel.Bancal@epfl.ch' >> /root/.ssh/authorized_keys

title2 "Setup to use mirror.switch.ch"
sed -i -e "s/http:\\/\\/archive.ubuntu.com/http:\\/\\/mirror.switch.ch\\/ftp\\/mirror\\/ubuntu/g" /etc/apt/sources.list

title2 "update and dist-upgrade"
apt-get -y update
apt-get -y dist-upgrade

title2 "purge chef and puppet"
apt-get -y purge chef chef-zero puppet puppet-common

title2 "Clean up"
apt-get -y autoremove
apt-get -y clean
apt-get -y autoclean

title1 "Finished !"
