from django.db import models

class Listing(models.Model):
    class Meta:
        db_table = 'wikivoyage_listings'

    title = models.CharField(max_length=128)
    language = models.CharField(max_length=2)
    article = models.CharField(max_length=128)
    type = models.CharField(max_length=64)
    description = models.CharField(max_length=4096)
    latitude = models.DecimalField(max_digits=10, decimal_places=8)
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
