% New client ENACdrives : Workflow
% SB, ND, SN, PDJ (ENAC-IT)


COMMON
======

* Project repo : git@gitlab.epfl.ch:bancal/MyDrives.git
* Release version : set in enacdrives/client/utility.py (CONST.VERSION & CONST.VERSION_DATE)


LINUX
=====


Compile & Package
-----------------

~~~ bash
~/Projects/enacdrives/tools/build_enacdrives_deb.sh
~~~


Send package to enacrepo.epfl.ch
--------------------------------

~~~ bash
cd ~/Projects/enacdrives/deb_building/
sshfs enacit1@enacrepo:/data/web/enacrepo/ enacrepo.epfl.ch/

reprepro -b enacrepo.epfl.ch/public/ list precise
reprepro -b enacrepo.epfl.ch/public/ list trusty
reprepro -b enacrepo.epfl.ch/public/ list utopic
reprepro -b enacrepo.epfl.ch/public/ list vivid
reprepro -b enacrepo.epfl.ch/public/ list wily
reprepro -b enacrepo.epfl.ch/public/ list xenial

reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb precise enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb precise enacdrives_amd64.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb trusty enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb trusty enacdrives_amd64.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb utopic enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb utopic enacdrives_amd64.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb vivid enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb vivid enacdrives_amd64.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb wily enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb wily enacdrives_amd64.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb xenial enacdrives_i386.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase includedeb xenial enacdrives_amd64.deb
~~~


WINDOWS
=======

<SB>

~~~ bash
enacdrives -n nas3_enac-it_files
cp -R /home/sbancal/Projects/enacdrives/client/ /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/
rm -rf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/exe.win32-3.4
~~~

~~~
cd Y:\common\ENACdrives\src\client
Y:
python setup.py build
~~~

Test ...

Make a zip (-> PortableApps)
~~~ bash
export VERSION=$(PYTHONPATH=/usr/lib/python3/dist-packages python3 ~/Projects/enacdrives/client/tell_version.py); echo $VERSION

pushd ~/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/
rm -rf ENACdrives-${VERSION} ENACdrives-${VERSION}.zip
cp -r exe.win32-3.4 ENACdrives-${VERSION}
zip -r ENACdrives-${VERSION}.zip ENACdrives-${VERSION}/
popd
~~~

Give it to IT2 for Packaging
~~~ bash
rm -rf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built
mv /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/exe.win32-3.4 /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built
rm -rf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built/enacdrives.conf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built/enacdrives.cache /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built/execution_output.txt
~~~

<ND> contenu du fichier \\enac1files\enac-it\common\ENACdrives\Windows\readme.txt :

Manuel  de création du fichier SetupENACdrives-version.exe

Installer Inno Setup à partir de http://www.jrsoftware.org/isinfo.php
La version de base non-unicode sans package supplémentaire fonctionne très bien.

Depuis Inno Setup, ouvrez le fichier \\enac1files.epfl.ch\ENAC-IT\common\ENACdrives\Windows\script.iss

Adaptez le numéro de version:
#define MyAppVersion "0.2.1"

Cliquez le menu Build > Compile
Le setup est généré dans le répertoire \\enac1files.epfl.ch\ENAC-IT\common\ENACdrives\Windows
Pardois le génération échoue, jusqu'ici il a suffit de relancer.

Si l'icône change, Visual Studio permet d'extraire le .ico du .exe

Pour signer l'exe, l'envoyer via enacshare à codesigning@epfl.ch



MACOSX
======

~~~ bash
alias to_macp="rsync -e ssh -avH --exclude venv_py3 --exclude __pycache__  ~/Projects/enacdrives/client/ bancal@enac1mac2-NR:enacdrives_client/"
to_macp
~~~

~~~ bash
ssh enac1mac2-NR
cd ~/enacdrives_client/
rm -rf dist/*
mv enacdrives.py ENACdrives.py
python setup_osx.py py2app
cp /Users/bancal/anaconda/lib/libQtCore.4.dylib dist/ENACdrives.app/Contents/Resources/lib/
cp /Users/bancal/anaconda/lib/libQtGui.4.dylib dist/ENACdrives.app/Contents/Resources/lib/
cp /Users/bancal/anaconda/lib/libpng16.16.dylib dist/ENACdrives.app/Contents/Resources/lib/
cp /Users/bancal/anaconda/lib/libpng.dylib dist/ENACdrives.app/Contents/Resources/lib/
~~~

Test ... and give it to IT3 for Packaging via http://enacshare.epfl.ch (with Safari ... so that app is sent without preparing a zip)
Sending it through CIFS share kills UNIX permissions :(
