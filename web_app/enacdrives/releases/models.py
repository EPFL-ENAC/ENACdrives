from django.db import models


class Arch(models.Model):
    OS_WIN = "a"  # Windows
    OS_LIN = "b"  # Linux
    OS_OSX = "c"  # MacOSX
    OS_CHOICES = (
        (OS_WIN, "Windows"),
        (OS_LIN, "Linux"),
        (OS_OSX, "MacOSX"),
    )
    os = models.CharField(max_length=1, choices=OS_CHOICES, default=OS_WIN)

    current_installer = models.ForeignKey(
        "Installer", related_name="+", blank=True, null=True
    )

    def __str__(self):
        for os in self.OS_CHOICES:
            if self.os == os[0]:
                return os[1]
        raise Exception("Impossible status: os not found in OS_CHOICES!")

    class Meta:
        unique_together = ("os",)


class Installer(models.Model):
    upload_username = models.CharField(max_length=256)
    upload_date = models.DateTimeField()
    release_number = models.CharField(max_length=256)

    arch = models.ForeignKey("Arch")

    file_name = models.CharField(max_length=256)
    storage_name = models.CharField(max_length=256)

    def __str__(self):
        return self.file_name
