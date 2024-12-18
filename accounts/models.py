from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    date_of_birth = models.DateField(null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    school = models.CharField(max_length=255, null=True, blank=True)
    region = models.CharField(max_length=100, choices=[
        ('region_1', 'Регион 1'),
        ('region_2', 'Регион 2'),
        ('region_3', 'Регион 3'),
        ('region_4', 'Регион 4'),
    ], null=True, blank=True)
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('user', 'User')
    ]
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='user')

    def __str__(self):
        return self.email




