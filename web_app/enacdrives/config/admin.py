from django.contrib import admin

from .models import User, Group, Config


class ConfigAdmin(admin.ModelAdmin):
    fields = ['users', 'groups', 'data']
    list_display = ("get_users", "get_groups", "get_data")
    list_display_links = ("get_data",)
    
    def get_users(self, obj):
        return self.short(", ".join([u.name for u in obj.users.all()]), 20)
    get_users.short_description = 'Users'
    
    def get_groups(self, obj):
        return self.short(", ".join([g.name for g in obj.groups.all()]), 20)
    get_groups.short_description = 'Groups'
    
    def get_data(self, obj):
        return obj.data.replace("\n", "<br/>")
    get_data.short_description = "Data"
    get_data.allow_tags = True
    
    def short(self, string, max_length):
        if len(string) > max_length:
            return string[:max_length - 3] + "..."
        else:
            return string

admin.site.register(User)
admin.site.register(Group)
admin.site.register(Config, ConfigAdmin)
