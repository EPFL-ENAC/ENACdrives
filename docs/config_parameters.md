% mount_filers Config Parameters
% enac.epfl.ch - Samuel Bancal

# Config sources

- Script

  - default good practices options
  - server's config source URL

- User's (~/.mount_filers.conf)

  - user's entered values
    - userid & userid_label
    - mount stared
    - mount drive letters
  - user's own mount entries

- System's (/etc/mount_filers.conf) (usefull?)

  - admin's config URLs

- n-times Server's
  - all user's dedicated settings and mount entries

# Config parameters

## [config]

- import = URL | path
  - {VERSION} is substituted by mount_filer's version
  - {USERID} is substituted by value entered by user
  - {OS_FAMILY} is substituted by OS family ("Windows", "Ubuntu", "MacOSX", ...)
  - {OS_VERSION} is substituted by OS version ("7", "8", "8.1", "14.04", "10.10", ...)

## [global]

- userid_question = Text showed to ask user's identity (EPFL username)

- userid_validate_url = URL

  - {VERSION} is substituted by mount_filer's version
  - {USERID} is substituted by value entered by user
  - {OS_FAMILY} is substituted by OS family ("Windows", "Ubuntu", "MacOSX", ...)
  - {OS_VERSION} is substituted by OS version ("7", "8", "8.1", "14.04", "10.10", ...)

- userid = value entered by user
  (this is saved in User's config source to remember the value for future runs)

- userid_label = Label displayed when user's identity is set
  (this is saved in User's config source to remember the value for future runs)

- mnt_dir = Path used as parent's mountpoint. Substitutions available :

  - {DEFAULT_MNT_DIR}
  - {HOME_DIR}
  - {DESKTOP_DIR}
  - {LOCAL_USERNAME}
  - {LOCAL_GROUPNAME}

- Linux_CIFS_method = default method used for CIFS on Linux

  - mount.cifs : Linux's mount.cifs (requires sudo ability)
  - gvfs : Linux's gvfs-mount

- Linux_mount.cifs_filemode = filemode setting to use with mount.cifs method

- Linux_mount.cifs_dirmode = dirmode setting to use with mount.cifs method

- Linux_mount.cifs_options = options to use with mount.cifs method

- Linux_gvfs_symlink = boolean
  Enables the creation of a symbolic link to "local_path" after mount with gvfs method.
  default : True

- open_cmd = command to be used to open a folder

## [CIFS_realm]

- name = CIFS realm name

- username = username to use in this realm

- domain = domain to use in this realm

## [CIFS_mount]

- name = mount's name

- label = Label displayed

- realm = CIFS_realm used

- server_name = server name

- server_path = path to be mounted (uncludes share and may include subdir)

- local_path = path where to mount. Substitutions available :

  - {MNT_DIR}
  - {HOME_DIR}
  - {DESKTOP_DIR}
  - {LOCAL_USERNAME}
  - {LOCAL_GROUPNAME}

- stared = boolean
  default : False
- Linux_mount.cifs_filemode = filemode setting to use with mount.cifs method

- Linux_mount.cifs_dirmode = dirmode setting to use with mount.cifs method

- Linux_mount.cifs_options = options to use with mount.cifs method

- Windows_letter = letter
  Drive letter to use for the mount (only on Windows)

# OPEN QUESTIONS

- Will we need one day other input than the userid (username)?
