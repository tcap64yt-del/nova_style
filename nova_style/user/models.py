from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)

        if extra_fields.get("is_staff") is not True:
             raise ValueError("Superuser must have is_staff=True")

        return self.create_user(email, password, **extra_fields)

class Users(AbstractBaseUser):
    last_login = None

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    status = models.BooleanField(default=False)
    avatar_url = models.ImageField(upload_to='profile/',default='static/default.png',null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"

    def __str__(self):
        return self.email
         
class EmailOTP(models.Model):
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempts = models.PositiveSmallIntegerField(default=0)
    resend_count = models.PositiveSmallIntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return self.email
    
    class Meta:
        db_table ="email_otp"


class Addresses(models.Model):
    user=models.ForeignKey(Users,on_delete=models.CASCADE,related_name="addresses")
    name=models.CharField(max_length=255)
    addresses=models.TextField()
    phone=models.CharField(max_length=10)
    district=models.CharField(max_length=255)
    state=models.CharField(max_length=255)
    country=models.CharField(max_length=255)
    postal_code=models.CharField(max_length=6)
    is_default=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "addresses"

    def __str__(self):
        return self.name
    

