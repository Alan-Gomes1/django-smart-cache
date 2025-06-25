from django.db import models


class CachedModel(models.Model):
    value = models.CharField(max_length=100)

    def __str__(self):
        return self.value
