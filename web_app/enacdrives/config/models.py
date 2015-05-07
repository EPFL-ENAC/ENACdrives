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
    category = models.CharField(max_length=1, choices=CATEGORY_CHOICES, default=CAT_ALL)

    name = models.CharField(max_length=256)
    users = models.ManyToManyField(User, blank=True)
    epfl_units = models.ManyToManyField(EpflUnit, blank=True)
    ldap_groups = models.ManyToManyField(LdapGroup, blank=True)
    data = models.TextField(blank=True)

    def __str__(self):
        return str(self.id)
