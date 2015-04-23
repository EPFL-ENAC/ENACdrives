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
    users = models.ManyToManyField(User, blank=True)
    epfl_units = models.ManyToManyField(EpflUnit, blank=True)
    ldap_groups = models.ManyToManyField(LdapGroup, blank=True)
    data = models.TextField(blank=True)

    def __str__(self):
        return str(self.id)
