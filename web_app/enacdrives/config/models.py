from django.db import models


class User(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class EpflUnit(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class LdapGroup(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Config(models.Model):
    rank = models.IntegerField(default=0)
    enabled = models.BooleanField(default=True)

    CAT_ALL = "a"  # config applies to everyone
    CAT_USER = "b"  # config applies to some specified users
    CAT_EPFL_UNIT = "c"  # config applies to some specified EPFL Units
    CAT_LDAP_GROUP = "d"  # config applies to some specified LDAP Groups
    CATEGORY_CHOICES = (
        (CAT_ALL, "to All"),
        (CAT_USER, "to Users"),
        (CAT_EPFL_UNIT, "to EPFL Unit"),
        (CAT_LDAP_GROUP, "to LDAP Group"),
    )
    category = models.CharField(
        max_length=1, choices=CATEGORY_CHOICES, default=CAT_LDAP_GROUP
    )

    name = models.CharField(max_length=256)
    users = models.ManyToManyField(User, blank=True)
    epfl_units = models.ManyToManyField(EpflUnit, blank=True)
    ldap_groups = models.ManyToManyField(LdapGroup, blank=True)
    client_filter_version = models.CharField(max_length=256, default="", blank=True)
    client_filter_os = models.CharField(max_length=256, default="", blank=True)
    client_filter_os_version = models.CharField(max_length=256, default="", blank=True)
    data = models.TextField(blank=True)

    def __str__(self):
        return str(self.id)

    def pformat(self):
        return (
            "id: {id}\n"
            + "rank: {rank}\n"
            + "enabled: {enabled}\n"
            + "category: {category}\n"
            + "name: {name}\n"
            + "users: {users}\n"
            + "epfl_units: {epfl_units}\n"
            + "ldap_groups: {ldap_groups}\n"
            + "client_filter_version: {client_filter_version}\n"
            + "client_filter_os: {client_filter_os}\n"
            + "client_filter_os_version: {client_filter_os_version}\n"
            + "data: {data}\n"
        ).format(
            id=self.id,
            rank=self.rank,
            enabled=self.enabled,
            category=self.category,
            name=self.name,
            users=", ".join(self.users.all()),
            epfl_units=", ".join(self.epfl_units.all()),
            ldap_groups=", ".join(self.ldap_groups.all()),
            client_filter_version=self.client_filter_version,
            client_filter_os=self.client_filter_os,
            client_filter_os_version=self.client_filter_os_version,
            data=self.data,
        )
