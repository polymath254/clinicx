# customers/models.py

from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50, unique=True)  # unique customer code

    def __str__(self):
        return f"{self.name} ({self.code})"
