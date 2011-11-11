from django.db import models
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

########################################################################

class TaggedEntry(models.Model):
    """A tag on an entry."""
    name = models.CharField(max_length = 30, blank = True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey("content_type", "object_id")
    
    class Meta:
        abstract = True
        ordering = ["name"]
    
    def __unicode__(self):
        return self.name

class Username(TaggedEntry):
    pass

class Groupname(TaggedEntry):
    pass

class Config(models.Model):
    CONTEXT_CHOICES = (
        ("g", "Global"),
        ("u", "User"),
    )
    
    description = models.TextField(max_length = 150, blank = True)
    
    rank = models.PositiveIntegerField()
    
    username = generic.GenericRelation(Username)
    groupname = generic.GenericRelation(Groupname)
    
    context = models.CharField(max_length = 1, choices = CONTEXT_CHOICES, default = "g")
    profile = models.CharField(max_length = 30, blank = True)
    version = models.CharField(max_length = 20, blank = True)
    
    config = models.TextField(max_length=10000)
    
    def get_users(self):
        users = [u.__unicode__() for u in self.username.iterator()]
        return ", ".join(sorted(users))
    
    def get_groups(self):
        groups = [g.__unicode__() for g in self.groupname.iterator()]
        return ", ".join(sorted(groups))
    
    def set_users(self, users):
        current_users = set([u.__unicode__() for u in self.username.iterator()])
        
        expected_users = set()
        for u in users.split(","):
            expected_users.add(u.strip())
        
        # Add
        for u in expected_users:
            if u not in current_users:
                current_users.add(u)
                self.username.add(Username(name = u))
        
        # Remove
        for u in current_users:
            if u not in expected_users:
                user = self.username.get(name = u)
                user.delete()
        
        self.save()

    def set_groups(self, groups):
        current_groups = set([g.__unicode__() for g in self.groupname.iterator()])
        
        expected_groups = set()
        for g in groups.split(","):
            expected_groups.add(g.strip())
        
        # Add
        for g in expected_groups:
            if g not in current_groups:
                current_groups.add(g)
                self.groupname.add(Groupname(name = g))
        
        # Remove
        for g in current_groups:
            if g not in expected_groups:
                group = self.groupname.get(name = g)
                group.delete()
        
        self.save()

class ConfigAdmin(admin.ModelAdmin):
    fieldsets = [
        ("Who", {"fields": ["profile"]}),
        ("What", {"fields": ["config"]}),
    ]
    
    list_display = ("get_users", "get_groups", "profile", "config")
    list_display_links = list_display
