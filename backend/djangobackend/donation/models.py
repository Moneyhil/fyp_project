from django.db import models

# Create your models here.
class Admin1(models.Model):
    first_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def _str_(self):
        return self.first_name   


class Signup1(models.Model):
    first_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=11)
    password = models.CharField(max_length=128) 



    def __str__(self):
        return self.first_name