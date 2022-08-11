% New client ENACdrives : Workflow
% SB, ND, PDJ (ENAC-IT)

# COMMON

- Project repo :
  git@github.com:EPFL-ENAC/ENACdrives.git
- Release version :
  set in client/enacdrives/utility.py (CONST.VERSION & CONST.VERSION_DATE)

# LINUX

## Compile & Package

```bash
cd tools
bash build_enacdrives_deb.sh
```

## Send package to enacrepo.epfl.ch

```bash
cd ~/Projects/ENACdrives/deb_building/

cp ../debmake/enacdrives_X.Y.Z-U20.04.XX/enacdrives*.deb \
   ../debmake/enacdrives_X.Y.Z-U22.04.XX/enacdrives*.deb .

sshfs enacit1@enacrepo:/data/web/enacrepo/ enacrepo.epfl.ch/

reprepro -b enacrepo.epfl.ch/public/ list bionic
reprepro -b enacrepo.epfl.ch/public/ list focal
reprepro -b enacrepo.epfl.ch/public/ list jammy

reprepro -b enacrepo.epfl.ch/public/ ls enacdrives

# To prevent GPG not finding where to ask the password
# (absolutely necessary when doing through SSH)
echo UPDATESTARTUPTTY | gpg-connect-agent

reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase \
  includedeb bionic enacdrives_X.Y.Z-U20.04*.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase \
  includedeb focal enacdrives_X.Y.Z-U20.04*.deb
reprepro -b enacrepo.epfl.ch/public/ --ask-passphrase \
  includedeb jammy enacdrives_X.Y.Z-U22.04*.deb
```

# WINDOWS

<SB>

```bash
enacdrives -n nas3_enac-it_files
cp -R /home/sbancal/Projects/ENACdrives/client/ /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/
rm -rf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/exe.win32-3.4
```

```
cd Y:\common\ENACdrives\src\client
Y:
python setup.py build
```

Test ...

Make a zip (-> PortableApps)

```bash
export VERSION=$(/usr/bin/python3 ~/Projects/ENACdrives/client/tell_version.py); echo $VERSION

pushd ~/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/
rm -rf ENACdrives-${VERSION} ENACdrives-${VERSION}.zip
cp -r exe.win32-3.4 ENACdrives-${VERSION}
zip -r ENACdrives-${VERSION}.zip ENACdrives-${VERSION}/
popd
```

Give it to IT2 for Packaging

```bash
rm -rf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built
mv /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/src/client/build/exe.win32-3.4 /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built
rm -rf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built/enacdrives.conf /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built/enacdrives.cache /home/sbancal/Desktop/enac-it_on_enac1files/common/ENACdrives/Windows/built/execution_output.txt
```

<ND> contenu du fichier \\enac1files\enac-it\common\ENACdrives\Windows\readme.txt :

Manuel de création du fichier SetupENACdrives-version.exe

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

# MACOSX

On the Mac :

```bash
ssh -NR 22210:localhost:22 sbancal@salsa.epfl.ch
```

```bash
alias to_macp="rsync -e ssh -avH --exclude venv_py3 --exclude __pycache__  ~/Projects/ENACdrives/client/ bancal@enac1mac2-NR:enacdrives_client/"
to_macp
```

```bash
ssh enac1mac2-NR
build_enacdrives_osx () {
  cd ~/enacdrives_client/
  rm -rf dist/*
  mv enacdrives.py ENACdrives.py
  python setup_osx.py py2app
  cp /Users/bancal/anaconda/lib/libQtCore.4.dylib dist/ENACdrives.app/Contents/Resources/lib/
  cp /Users/bancal/anaconda/lib/libQtGui.4.dylib dist/ENACdrives.app/Contents/Resources/lib/
  cp /Users/bancal/anaconda/lib/libpng16.16.dylib dist/ENACdrives.app/Contents/Resources/lib/
  cp /Users/bancal/anaconda/lib/libpng.dylib dist/ENACdrives.app/Contents/Resources/lib/
}

build_enacdrives_osx
```

Test ... and give it to IT3 for Packaging via http://enacshare.epfl.ch (with Safari ... so that app is sent without preparing a zip)
Sending it through CIFS share kills UNIX permissions :(
