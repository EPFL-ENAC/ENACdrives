
Global :
========

* host enacdrives.epfl.ch on PROD server
* make Windows installer + doc
* make Linux package + doc
* make OSX installer + doc


web_app :
=========

* enac1files for main unit is not assigned to Y:

Monitoring :
------------

* Config.category has to match with Config.users, Config.epfl_units and Config.ldap_groups
* All {xyz} can be substitued in config


client :
========

* Check for update ++
* add menus for
  + Documentation link
  + Show/Hide entries
* bad syntax in config received when user is on public-epfl Wifi with no VPN
* check server is responding for each CIFS_mount (show msg related to VPN if not)
* GUI message if no CIFS_mount is available
* CLI
* enacit1logs

Windows
-------

* .conf and .cache moved to %USERPROFILE%
* If a mount is already done before launch enacdrives and the drive letter is not assigned -> user doesn't know where it's mounted
* Windows XP is KO

Linux
-----

* switch mount.cifs <-> gvfs and some shares are still mounted

client test :
-------------

* on public-epfl
* on Eduroam
* no network
* low bandwidth (timeout)
