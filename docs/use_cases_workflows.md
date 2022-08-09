% mount_filers Use Cases Workflows
% enac.epfl.ch - Samuel Bancal

## 2015.01.20 - SB ● 1st run GUI scenario #1 (abandoned)

```bash
mount_filers -l
```

```state
[config]
import = http://enacXXX.epfl.ch/mount_filers/config?version=__VERSION__
```

```operation
get http://enacXXX.epfl.ch/mount_filers/config?version=0.1
```

```out
[config]
import = http://enacXXX.epfl.ch/mount_filers/config?username=__EPFL_USERNAME__&version=__VERSION__

[variable]
name = __EPFL_USERNAME__
label = your EPFL username
constraint = lowercase
validate = http://enacXXX.epfl.ch/mount_filers/validate?username=__EPFL_USERNAME__
```

```operation
Save that config to $HOME/.mount_filers.cache/md5_hash

Want to get new config URL http://enacXXX.epfl.ch/mount_filers/config?username=__EPFL_USERNAME__&version=__VERSION__
Holds until __EPFL_USERNAME__ is filled
Ask "Enter your EPFL username :" -> __EPFL_USERNAME__

When user has filled __EPFL_USERNAME__ : validate with http://enacXXX.epfl.ch/mount_filers/validate?username=__EPFL_USERNAME__
If not valid, show error msg and Holds until __EPFL_USERNAME__ is filled

Free every operation waiting on __EPFL_USERNAME__
get http://enacXXX.epfl.ch/mount_filers/config?username=bancal&version=0.1
```

```out
[message]
label = user : Samuel Bancal (bancal)
rank = 1
reset = __EPFL_USERNAME__
reset = __EPFL_SCIPER__
reset = __EPFL_DOMAIN__

[variable]
name = __EPFL_SCIPER__
label = your Last digit of your SCIPER
value = 9

[variable]
name = __EPFL_DOMAIN__
label = your EPFL Authentication Domain
value = intranet

[CIFS_mount]
name = private
label = bancal@files9 (individuel)
server_name = files9.epfl.ch
server_path = data/bancal
local_path = __MNT_DIR__/bancal_on_files9

[CIFS_mount]
name = enacit1_pm_enacproj
label = enacit1@enacproj
server_name = enacproj.epfl.ch
server_path = enacit1
local_path = __MNT_DIR__/enacit1_on_enacproj

[CIFS_mount]
name = doclinux
label = doclinux@enac1web
username = doclinux
domain = WORKGROUP
auth_realm = DOCLINUX
server_name = enac1web.epfl.ch
server_path = doclinux
local_path = __MNT_DIR__/doclinux_on_enac1web

[CIFS_mount]
name = bak_machines
label = bak_machines@enac1na2-g1
server_name = enac1na2-g1.epfl.ch
server_path = bak_machines
local_path = __MNT_DIR__/bak_machines_on_enac1na2-g1

[CIFS_mount]
name = lab_enac-it_tier1
label = enac-it@enacfiles1 (collectif tier1)
server_name = enacfiles1.epfl.ch
server_path = enac-it
local_path = __MNT_DIR__/enac-it_on_enacfiles1
mount.cifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm

[CIFS_mount]
name = lab_enac-it_tier2
label = enac-it@enacfiles2 (collectif tier2)
server_name = enacfiles2.epfl.ch
server_path = enac-it
local_path = __MNT_DIR__/enac-it_on_enacfiles2
mount.cifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm

[CIFS_mount]
name = lab_iie-ge_tier1
label = iie-ge@enacfiles1 (collectif tier1)
server_name = enacfiles1.epfl.ch
server_path = iie-ge
local_path = __MNT_DIR__/iie-ge_on_enacfiles1
mount.cifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm

[CIFS_mount]
name = lab_iie-ge_tier2
label = iie-ge@enacfiles2 (collectif tier2)
server_name = enacfiles2.epfl.ch
server_path = iie-ge
local_path = __MNT_DIR__/iie-ge_on_enacfiles2
mount.cifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
```

```operation
Save that config to $HOME/.mount_filers.cache/md5_hash

Display message rank 1

List all CIFS_Mount entries and wait for user interaction (mount/umount/open/star)
```

## 2015.01.22 - SB ● 1st run GUI scenario #2 (take it)

```bash
mount_filers -l
```

```state
[config]
import = http://enacXXX.epfl.ch/mount_filers/config?version={VERSION}&username={USERID}

[global]
userid_question = What is your EPFL username?
userid_validate_url = http://enacXXX.epfl.ch/mount_filers/validate?username={USERID}
mnt_dir = DEFAULT_MNT_DIR[OS]
open_cmd = DEFAULT_OPEN_CMD[OS]
Linux_CIFS_method = gvfs
mount.cifs_filemode = 0770
mount.cifs_dirmode  = 0770
mount.cifs_options = rw,nobrl,noserverino,iocharset=utf8
gvfs_symlink = true
```

```operation
ask for "EPFL username" -> userid
Validate with http://enacXXX.epfl.ch/mount_filers/validate?username={USERID} . 2 possible answers :
```

```out
valid = False
```

```out
valid = True
userid = bancal
userid_label = Bancal Samueé ENAC-IT-IIE-GE
```

```operation
if not valid: ask again

save the following to $HOME/.mount_filers.conf
```

```out
[config]
userid = bancal
userid_label = Bancal Samuel ENAC-IT|IIE-GE
```

```operation
get http://enacXXX.epfl.ch/mount_filers/config?username=bancal&version=0.1
cache it in $HOME/.mount_filers.cache/md5_hash
```

```out
[CIFS_realm]
name = EPFL
username = bancal
domain = intranet

[CIFS_realm]
name = DOCLINUX
username = doclinux
domain = WORKGROUP

[CIFS_mount]
name = private
label = bancal on files9 (individuel)
realm = EPFL
server_name = files9.epfl.ch
server_path = data/bancal
local_path = {MNT_DIR}/bancal_on_files9
stared = false
Windows_letter = Z

[CIFS_mount]
name = enacit1_on_enacproj
label = enacit1 on enacproj
realm = EPFL
server_name = enacproj.epfl.ch
server_path = enacit1
local_path = {MNT_DIR}/enacit1_on_enacproj
stared = false

[CIFS_mount]
name = doclinux
label = doclinux on enac1web
realm = DOCLINUX
server_name = enac1web.epfl.ch
server_path = doclinux
local_path = {MNT_DIR}/doclinux_on_enac1web
stared = false

[CIFS_mount]
name = bak_machines
label = bak_machines on enac1na2-g1
realm = EPFL
server_name = enac1na2-g1.epfl.ch
server_path = bak_machines
local_path = {MNT_DIR}/bak_machines_on_enac1na2-g1
stared = false

[CIFS_mount]
name = lab_enac-it_tier1
label = enac-it on enacfiles1 (collectif tier1)
realm = EPFL
server_name = enacfiles1.epfl.ch
server_path = enac-it
local_path = {MNT_DIR}/enac-it_on_enacfiles1
mount.cifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
stared = false
Windows_letter = U

[CIFS_mount]
name = lab_enac-it_tier2
label = enac-it on enacfiles2 (collectif tier2)
realm = EPFL
server_name = enacfiles2.epfl.ch
server_path = enac-it
local_path = {MNT_DIR}/enac-it_on_enacfiles2
mount.cifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
stared = false
Windows_letter = V

[CIFS_mount]
name = lab_iie-ge_tier1
label = iie-ge on enacfiles1 (collectif tier1)
realm = EPFL
server_name = enacfiles1.epfl.ch
server_path = iie-ge
local_path = {MNT_DIR}/iie-ge_on_enacfiles1
mount.cifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
stared = false

[CIFS_mount]
name = lab_iie-ge_tier2
label = iie-ge on enacfiles2 (collectif tier2)
realm = EPFL
server_name = enacfiles2.epfl.ch
server_path = iie-ge
local_path = {MNT_DIR}/iie-ge_on_enacfiles2
mount.cifs_options = rw,nobrl,noserverino,iocharset=utf8,sec=ntlm
stared = false
```

```operation
List all *_mount entries and wait for user interaction (mount/umount/open/star)
Display message before "private"
```
