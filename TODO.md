
Global :
========

* host enacdrives.epfl.ch on PROD server
* make Windows installer + doc
* make Linux package + doc
* make OSX installer + doc


web_app :
=========


client :
========

* Check for update ++
* add menus for
  + Documentation link
  + Show/Hide entries
* check server is responding for each CIFS_mount (show msg related to VPN if not)
* GUI message if no CIFS_mount is available
* CLI
* enacit1logs


client test :
-------------

* no network
* low bandwidth (timeout)


Monitoring :
------------

* Config.category has to match with Config.users, Config.epfl_units and Config.ldap_groups
* All {xyz} can be substitued in config
