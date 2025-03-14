from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("The Phone number field must be set")

        email = self.normalize_email(email) if email else None
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password, email=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(phone_number, email=email, password=password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255, null=False)
    alternate_name=models.CharField(max_length=255,null=True)
    birthdate=models.DateField(null=True,blank=True)
    country=models.CharField(max_length=255,null=True,blank=True)
    phone_number = models.CharField(max_length=20, unique=True, null=False)
    email = models.EmailField(max_length=255, blank=True, null=True)
    profile=models.ImageField(upload_to='profile_images/', blank=True, null=True,default='../static/images/default_profile.jpg')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "phone_number"
    REQUIRED_FIELDS = ["email"]  # Superusers must have an email

    def __str__(self):
        return self.full_name
