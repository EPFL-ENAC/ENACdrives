from django.contrib import admin

from .models import User, EpflUnit, LdapGroup, Config


class ConfigAdmin(admin.ModelAdmin):
    fieldsets = (
        ("What", {"fields": (("name", "enabled"), "rank", "data")}),
        ("Who", {"fields": ("category", "users", "epfl_units", "ldap_groups")}),
        ("Client Filter", {"fields": ("client_filter_version", "client_filter_os", "client_filter_os_version")}),
    )
    list_display = ("name", "enabled", "rank", "category", "get_users", "get_epfl_units", "get_ldap_groups", "get_client_filter", "get_data")
    list_display_links = ("name", "get_data")
    ordering = ("rank", )

    def get_users(self, obj):
        return ", ".join([u.name for u in obj.users.all()])
    get_users.short_description = "Users"

    def get_epfl_units(self, obj):
        return ", ".join([g.name for g in obj.epfl_units.all()])
    get_epfl_units.short_description = "EPFL Units"

    def get_ldap_groups(self, obj):
        return ", ".join([g.name for g in obj.ldap_groups.all()])
    get_ldap_groups.short_description = "Ldap Groups"

    def get_data(self, obj):
        return obj.data.replace("\n", "<br/>")
    get_data.short_description = "Data"
    get_data.allow_tags = True

    def get_client_filter(self, obj):
        the_list = []
        if obj.client_filter_version != "":
            the_list.append("<nobr>version is '{}'</nobr>".format(obj.client_filter_version))
        if obj.client_filter_os != "":
            the_list.append("<nobr>os is '{}'</nobr>".format(obj.client_filter_os))
        if obj.client_filter_os_version != "":
            the_list.append("<nobr>os_version is '{}'</nobr>".format(obj.client_filter_os_version))
        if len(the_list) == 0:
            return "None"
        else:
            return " and <br>".join(the_list)
    get_client_filter.short_description = "Client Filter"
    get_client_filter.allow_tags = True

    def short(self, string, max_length):
        if len(string) > max_length:
            return string[:max_length - 3] + "..."
        else:
            return string

admin.site.register(User)
admin.site.register(EpflUnit)
admin.site.register(LdapGroup)
admin.site.register(Config, ConfigAdmin)
