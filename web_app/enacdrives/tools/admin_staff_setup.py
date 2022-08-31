import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "enacdrives.settings"

my_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(my_path)

from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist


EXPECTED_ADMINS = (
    "bancal",
    "bonjour",
    "dameylan",
    "nepa",
    "pdejesus",
)


def main():
    now = timezone.now()
    for adm_name in EXPECTED_ADMINS:
        try:
            u = User.objects.get(username=adm_name)
            u.is_superuser = True
            u.is_staff = True
            u.is_active = True
            u.save()
            print("Set user '{0}' as admin.".format(adm_name))
        except ObjectDoesNotExist:
            u = User(
                username=adm_name,
                is_superuser=True,
                is_staff=True,
                is_active=True,
                date_joined=now,
            )
            u.save()
            print("Added user '{0}' as admin.".format(adm_name))


if __name__ == "__main__":
    main()
