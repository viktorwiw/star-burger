from django.db import models

class AddressCache(models.Model):
    address = models.CharField("Адрес", max_length=255, unique=True, db_index=True)
    lat = models.FloatField("Широта", null=True)
    lon = models.FloatField("Долгота", null=True)
    updated_at = models.DateTimeField("Дата обновления", auto_now=True)

    def __str__(self):
        return f"{self.address} ({self.lat}, {self.lon})"
