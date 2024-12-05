from django.contrib.auth.models import AbstractUser
from django.db import models

ORDINARY_USER, MANAGER, ADMIN = ("ordinary_user", "manager", "admin")
VIA_EMAIL, VIA_PHONE = ("via_email", "via_phone")
NEW, CODE_VERIFIED, DONE, PHOTO_STEP = ("new", "code_verified", "done", "photo_step")

class User(AbstractUser):
    USER_ROLES =  (
        (ORDINARY_USER, ORDINARY_USER),
        (MANAGER, MANAGER),
        (ADMIN, ADMIN),
    )

    AUTH_TYPES_CHOICES = (
        (VIA_EMAIL, VIA_PHONE),
        (VIA_PHONE, VIA_PHONE),
    )
    AUTH_STATUS = (
        (NEW, NEW),
        (CODE_VERIFIED, CODE_VERIFIED),
        (DONE, DONE),
        (PHOTO_STEP, PHOTO_STEP),
    )

    user_roles = models.CharField(max_length=31, choices=USER_ROLES, default=ORDINARY_USER)
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPES_CHOICES)
    auth_status = models.CharField(max_length=31, choices=AUTH_STATUS, default=NEW)
    email = models.EmailField(unique=True, blank=True, null=True)
    phone_number = models.CharField(max_length=13, blank=True, null=True)
    photo = models.ImageField(upload_to='user/photos', blank=True, null=True
                              )