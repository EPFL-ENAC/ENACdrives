# ENACdrives

## Linux

### Prepare env

```bash
conda install distro
```

### Run

```bash
cd client/
export PYTHONPATH=$(pwd)
python3 bin/enacdrives
```

## Windows

### Prepare env

- install Miniconda

```powershell
conda create -n py310 python=3.10
conda activate py310
conda install distro
conda install pyinstaller
conda install pywin32
conda install pyqt=5
setx PYTHONPATH C:\ThePathToThe\enacdrives\client
# You'll have to run a new terminal so that this is taken
```

### Run

```powershell
cd client/
python bin/enacdrives
```

### Build

```powershell
cd client
pyinstaller -y enacdrives.spec
copy share\pixmaps\enacdrives\* dist\enacdrives\
cd dist\enacdrives\_internal
move-Item .\MSVCP140.dll, .\MSVCP140_1.dll ..
```

- Compress the folder `dist/enacdrives` to `dist/enacdrives.zip`
- send it to Nicolas Dubois so that he :
  - gets it signed (EPFL)
  - prepares a nice installer
