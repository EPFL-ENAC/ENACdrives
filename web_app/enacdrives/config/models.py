from django.db import models


class User(models.Model):
    name = models.CharField(max_length=256)
    
    def __str__(self):
        return self.name


class Group(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Config(models.Model):
    users = models.ManyToManyField(User, blank=True)
    groups = models.ManyToManyField(Group, blank=True)
    data = models.TextField(blank=True)

    def __str__(self):
        return str(self.id)
