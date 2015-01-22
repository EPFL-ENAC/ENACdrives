% mount_filers Config Parameters
% enac.epfl.ch - Samuel Bancal


# Config sources

* Script
    * default options
    * server's config source URL

* User's (~/.mount_filers.conf)
    * user's entered values
        * config's userid
        * mount stared
        * mount drive letters
    * user's own mount entries

* System's (/etc/mount_filers.conf) (usefull?)
    * admin's config URLs

* n-times Server's
    * all user's dedicated settings and mount entries


# Config parameters

## [config]

* name = unique name used to match between config sources and user entries saved
    in user's config source. This prevent from asking again username at every run.

* import = URL | path
    * {VERSION} is substituted by mount_filer's version
    * {USERID} is substituted by value entered by user if "userid_label" is specified
    * {OS_FAMILY} is substituted by OS family ("Windows", "Ubuntu", "MacOSX", ...)
    * {OS_VERSION} is substituted by OS version ("7", "8", "8.1", "14.04", "10.10", ...)

* userid_label = Label showed to ask user's identity (EPFL username)
    if specified, a textfield is displayed and has to be filled before importing the config
    if not specified, the config is imported directly

* userid_validate_url = URL
    * {VERSION} is substituted by mount_filer's version
    * {USERID} is substituted by value entered by user if "userid_label" is specified
    * {OS_FAMILY} is substituted by OS family ("Windows", "Ubuntu", "MacOSX", ...)
    * {OS_VERSION} is substituted by OS version ("7", "8", "8.1", "14.04", "10.10", ...)

* userid_value = value entered by user (this is used in User's config source)


## [global]

* CIFS_method = default method used for CIFS
    mount.cifs : Linux's mount.cifs
    gvfs : Linux's gvfs-mount
    mount_smbfs : Mac OSX's mount_smbfs
    XXX : Windows's XXX

* mnt_dir = Path used as parent's mountpoint.

* mount.cifs_filemode = options to use with mount.cifs method

* mount.cifs_dirmode  = options to use with mount.cifs method

* mount.cifs_options = options to use with mount.cifs method

* gvfs_symlink = boolean
    Enables the creation of a symbolic link to "local_path" after mount with gvfs method.
    default : True


## [message]

* label = End used message to be displayed

* place_before = x_mount's name where to place this message


## [CIFS_realm]

* name = CIFS realm name

* username = username to use in this realm

* domain = domain to use in this realm


## [CIFS_mount]

* name = mount's name

* label = Label displayed

* realm = CIFS_realm used

* server_name = server name

* server_path = path to be mounted (uncludes share and may include subdir)

* local_path = path where to mount
    * {MNT_DIR} is substituted

* mount.cifs_options = options to use with mount.cifs method





