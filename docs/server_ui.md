% mount_filers Server's User Interface
% enac.epfl.ch - Samuel Bancal

# ENAC-IT admin UI

## Usage

- Give access to EPFL centralized storage (NAS3)
- Give access to ENAC storage (enacproj.epfl.ch, ...)
- Give access to unit's storage when they ask to (-> Documentation & Communication should let it know!)

- Has to use Tequila

## URLs

### /adm/

List of config entries with : \* Description = Admin comprehensible description of the entry

    * Context = Global|User
        * Global : is given once per config request
        * User : is given 0 to n-times depending on user's group membership (LDAP & AD)

    * Users = list of users who will inherit that entry

    * LDAP_Groups = list of LDAP groups who will inherit that entry

    * AD_Groups = list of AD groups who will inherit that entry

    * Version = Expression that filters in/out clients depending of their client version
        * < 1.0.0 # olds clients
        * >= 1.2.0 # ...

    * Config = config string to be sent

Entries can be
_ added
_ dragged to change the order \* deleted

### /adm/edit

Every fields described above can be configured.

# End-user admin UI

## Usage

- Customize each mount entries (overides default values set by ENAC-IT admins):

  - stared
  - Windows_letter
  - hide unwanted (will be hidden on every client with a notice "n entries are hidden. Go <here>(http://enacXXX.epfl.ch/mount_filers/) to un-hide them.")

- View the config that corresponds to him

- Has to use Tequila

## URLs

### /

View config that corresponds to the authenticated user

For each entry, possibility to:
_ star
_ change the Windows_letter \* check "hide"

# OPEN QUESTIONS

- Should we add Version to entries?
- Is End-user admin UI usefull?
