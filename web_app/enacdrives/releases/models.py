from django.db import models


class Installer(models.Model):
    upload_username = models.CharField(max_length=256)
    upload_date = models.DateTimeField()
    release_number = models.CharField(max_length=256)
    
    OS_WIN = "a"  # Windows
    OS_LIN = "b"  # Linux
    OS_OSX = "c"  # MacOSX
    OS_CHOICES = (
        (OS_WIN, "Windows"),
        (OS_LIN, "Linux"),
        (OS_OSX, "MacOSX"),
    )
    os = models.CharField(max_length=1, choices=OS_CHOICES, default=OS_WIN)
    
    file_name = models.CharField(max_length=256)
    storage_name = models.CharField(max_length=256)
    
    enabled = models.BooleanField(default=False)

    def __str__(self):
        return "{} {} {}".format(self.os, self.file_name, self.storage_name)
