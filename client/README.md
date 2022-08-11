# ENACdrives

## Linux

### Prepare env :

```bash
conda install distro
```

### Run :

```bash
cd client/
export PYTHONPATH=$(pwd)
python3 bin/enacdrives
```

## Windows

### Prepare env :

- install Anaconda

```bash
conda install distro
conda install pyinstaller
setx PYTHONPATH C:\ThePathToThe\enacdrives\client
# You'll have to run a new terminal so that this is taken
```

### Run :

```bash
cd client/
python bin/enacdrives
```

### Build :

```bash
cd client
pyinstaller -y enacdrives.spec
```

- Compress the folder `dist/enacdrives` to `dist/enacdrives.zip`
- send it to Nicolas Dubois so that he :
  - gets it signed (EPFL)
  - prepares a nice installer
