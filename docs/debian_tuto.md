https://wiki.debian.org/IntroDebianPackaging

# 0. Pre-requisite

```bash
sudo apt-get install build-essential devscripts debhelper
cd ~/tmp/pkg_deb
```

# 0. Get upstream tarball

```bash
wget http://code.liw.fi/hithere/hithere-1.0.tar.gz
```

# 1. rename the upstream tarball

```bash
mv hithere-1.0.tar.gz hithere_1.0.orig.tar.gz
```

# 2. Unpack the upstram tarball

```bash
tar -xf hithere_1.0.orig.tar.gz
cd hithere-1.0
```

# 3. Add Debian packaging files

```bash
mkdir debian
```

## debian/changelog

```bash
dch --create -v 1.0-1 --package hithere
```

```snip
hithere (1.0-1) UNRELEASED; urgency=medium

  * Initial release.

 -- Bancal Samuel <sbancal@enacit1pc4>  Fri, 19 Jun 2015 11:18:33 +0200
```

## debian/compat

```snip
9
```

## debian/control

```snip
Source: hithere
Maintainer: Lars Wirzenius <liw@liw.fi>
Section: misc
Priority: optional
Standards-Version: 3.9.2
Build-Depends: debhelper (>= 9)

Package: hithere
Architecture: any
Depends: ${shlibs:Depends}, ${misc:Depends}
Description: greet user
 hithere greets the user, or the world.
```

## debian/copyright

```snip

```

## debian/rules (tabbed)

```snip
#!/usr/bin/make -f
%:
	dh $@
```

## debian/source/format

```snip
3.0 (quilt)
```

# 4. Build the package

```bash
debuild -us -uc
```

```snip
make[1]: Entering directory `/home/sbancal/tmp/pkg_deb/hithere-1.0'
install hithere /home/sbancal/tmp/pkg_deb/hithere-1.0/debian/hithere/usr/local/bin
install: cannot create regular file ‘/home/sbancal/tmp/pkg_deb/hithere-1.0/debian/hithere/usr/local/bin’: No such file or directory
make[1]: *** [install] Error 1
make[1]: Leaving directory `/home/sbancal/tmp/pkg_deb/hithere-1.0'
dh_auto_install: make -j1 install DESTDIR=/home/sbancal/tmp/pkg_deb/hithere-1.0/debian/hithere AM_UPDATE_INFO_DIR=no returned exit code 2
make: *** [binary] Error 2
dpkg-buildpackage: error: fakeroot debian/rules binary gave error exit status 2
debuild: fatal error at line 1364:
dpkg-buildpackage -rfakeroot -D -us -uc failed
```

FIX : tell make to install into /usr , not into /usr/local

## debian/rules (tabbed)

```snip
#!/usr/bin/make -f
%:
        dh $@

override_dh_auto_install:
        $(MAKE) DESTDIR=$$(pwd)/debian/hithere prefix=/usr install
```

Try again :

```bash
debuild -us -uc
```

```snip
make[1]: Entering directory `/home/sbancal/tmp/pkg_deb/hithere-1.0'
/usr/bin/make DESTDIR=$(pwd)/debian/hithere prefix=/usr install
make[2]: Entering directory `/home/sbancal/tmp/pkg_deb/hithere-1.0'
install hithere /home/sbancal/tmp/pkg_deb/hithere-1.0/debian/hithere/usr/bin
install: cannot create regular file ‘/home/sbancal/tmp/pkg_deb/hithere-1.0/debian/hithere/usr/bin’: No such file or directory
make[2]: *** [install] Error 1
make[2]: Leaving directory `/home/sbancal/tmp/pkg_deb/hithere-1.0'
make[1]: *** [override_dh_auto_install] Error 2
make[1]: Leaving directory `/home/sbancal/tmp/pkg_deb/hithere-1.0'
make: *** [binary] Error 2
dpkg-buildpackage: error: fakeroot debian/rules binary gave error exit status 2
debuild: fatal error at line 1364:
dpkg-buildpackage -rfakeroot -D -us -uc failed
```

FIX : Add missing dirs

## debian/hithere.dirs

```snip
usr/bin
usr/share/man/man1
```

Try again :

```bash
debuild -us -uc
```

```snip
dpkg-deb: building package `hithere' in `../hithere_1.0-1_amd64.deb'.
 dpkg-genchanges  >../hithere_1.0-1_amd64.changes
dpkg-genchanges: including full source code in upload
 dpkg-source --after-build hithere-1.0
dpkg-buildpackage: full upload (original source is included)
Now running lintian...
E: hithere changes: changed-by-address-malformed Bancal Samuel <sbancal@enacit1pc4>
W: hithere source: ancient-standards-version 3.9.2 (current is 3.9.5)
E: hithere: debian-changelog-file-contains-invalid-email-address sbancal@enacit1pc4
W: hithere: new-package-should-close-itp-bug
W: hithere: copyright-without-copyright-notice
W: hithere: zero-byte-file-in-doc-directory usr/share/doc/hithere/copyright
Finished running lintian.
```

```bash
ls -l ..
```

```snip
drwxrwxr-x 3 sbancal sbancal 4096 Jun 22 10:08 hithere-1.0
-rw-r--r-- 1 sbancal sbancal 2759 Jun 22 10:08 hithere_1.0-1_amd64.build
-rw-r--r-- 1 sbancal sbancal 1371 Jun 22 10:08 hithere_1.0-1_amd64.changes
-rw-r--r-- 1 sbancal sbancal 2820 Jun 22 10:08 hithere_1.0-1_amd64.deb
-rw-r--r-- 1 sbancal sbancal  733 Jun 22 10:08 hithere_1.0-1.debian.tar.gz
-rw-r--r-- 1 sbancal sbancal  732 Jun 22 10:08 hithere_1.0-1.dsc
-rw-rw-r-- 1 sbancal sbancal  616 Jun 19 10:55 hithere_1.0.orig.tar.gz
```
