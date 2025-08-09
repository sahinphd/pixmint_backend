from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

class UserManager(BaseUserManager):
    def create_user(self, userid, name, email, password=None, refarcode=None):
        if not email:
            raise ValueError("Email is required")
        user = self.model(
            userid=userid, 
            name=name, 
            email=self.normalize_email(email),
            refarcode=refarcode
            )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, userid, name, email, password):
        user = self.create_user(userid, name, email, password)
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    id = models.AutoField(primary_key=True)
    userid = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    usercode = models.CharField(max_length=20, unique=True, blank=True, null=True)
    refarcode = models.CharField(max_length=20,  blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'userid'
    REQUIRED_FIELDS = ['name', 'email']

    def __str__(self):
        return self.userid

    def has_perm(self, perm, obj=None): return True
    def has_module_perms(self, app_label): return True
    @property
    def is_staff(self): return self.is_admin
