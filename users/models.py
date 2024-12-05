import random
import uuid
from datetime import datetime, timedelta
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.regex_helper import normalize
from rest_framework_simplejwt.tokens import RefreshToken

from shared.models import BaseModel

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
        (VIA_EMAIL, VIA_EMAIL),
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
    photo = models.ImageField(upload_to='user/photos', blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg'])])

    def __str__(self):
        return self.username

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def create_verify_code(self, verify_type):
        code = "".join([str(random.randint(0, 100)) for _ in range(4)])
        UserConfirmation.objects.create(
            user_id = self.id,
            verify_type=verify_type,
            code = code,
        )

        return code

    def chek_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4().__str__().split('-')[-1]}."
            if User.objects.filter(username=temp_username).exists():
                temp_username = f"{temp_username}{random.randint(0, 10)}"
            self.username = temp_username

    def chek_email(self):
        if self.email:
            normalize_email = self.email.lower()
            self.email = normalize_email

    def chek_pass(self):
        if not self.password:
            temp_password = f"password-{uuid.uuid4().__str__().split('-')[-1]}."
            self.password = temp_password

    def hashing_password(self):
        if not self.password.startswith("pbkdf2_sha256"):
            self.set_password(self.password)

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh_token": str(refresh),
        }

    def clean(self):
        self.chek_username()
        self.chek_email()
        self.hashing_password()
        self.token()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()
        super(User, self).save(*args, **kwargs)


PHONE_EXPIRE = 2
EMAIL_EXPIRE = 5

class UserConfirmation(BaseModel):
    TYPE_CHOICES = (
        (VIA_EMAIL, VIA_EMAIL),
        (VIA_PHONE, VIA_PHONE),
    )

    code = models.CharField(max_length=4)
    verify_type = models.CharField(max_length=1, choices=TYPE_CHOICES)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name = 'verify_codes')
    expiration_time = models.DateTimeField(blank=True, null=True)
    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return (self.user.__str__())

    def save(self , *args, **kwargs):
        if not self.pk:
            if self.verify_type == VIA_EMAIL:
                self.expiration_time = datetime.now() + timedelta(minutes=EMAIL_EXPIRE)
            else:
                self.expiration_time = datetime.now() + timedelta(minutes=PHONE_EXPIRE)

        super(UserConfirmation, self).save(*args, **kwargs)


