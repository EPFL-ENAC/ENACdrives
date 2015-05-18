
Priorities :
============

* must work on 2015-05-22
+ must work any soon
- will be fixed later

Global :
========

* host enacdrives.epfl.ch on PROD server
+ doc Windows installer
+ doc OSX installer
+ FIX Linux package "The package is of bad quality"
* Icon design


web_app :
=========

* enac1files for main unit is not assigned to Y:
* Upload new release
* Select the release to enable
* API for enacsoft.epfl.ch
    * know latest release number / os
    * know latest release date / os


Monitoring :
------------

+ Config.category has to match with Config.users, Config.epfl_units and Config.ldap_groups
+ All {xyz} can be substitued in config


client :
========

* Check for update ++
* check server is responding for each CIFS_mount (show msg related to VPN if not)
* "enacit1logs"
- GUI message if no CIFS_mount is available
- CLI
+ add menus for
  + Edit > Show/Hide entries
  - Edit > Preferences
    - Linux_CIFS_method
    - Linux_gvfs_symlink
    - Linux_mountcifs_dirmode
    - Linux_mountcifs_filemode
    - Linux_mountcifs_options

Windows
-------

* .conf and .cache moved to %USERPROFILE%
* If a mount is already done before launch enacdrives and the drive letter is not assigned -> user doesn't know where it's mounted
* Windows XP is KO


client test :
-------------

* on public-epfl
* on Eduroam
* no network
* low bandwidth (timeout)
