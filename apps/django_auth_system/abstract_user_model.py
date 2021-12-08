import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from django_auth_system.conf import settings


class CustomUserManager(BaseUserManager):
    def _create_user(self, **extra_fields):
        user_schema = settings.USER_MODEL_SCHEMA
        login_field = user_schema.get('USERNAME_FIELD')

        if extra_fields.get(login_field) is None:
            raise ValueError('The USERNAME_FIELD must be set')

        fields = user_schema.get('FIELDS')
        for name, field in fields.items():
            if field.get('field_type') == 'EmailField':
                extra_fields[name] = self.normalize_email(
                                        extra_fields.get(name)
                                    )

        password = extra_fields.pop('password')
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(**extra_fields)

    def create_superuser(self, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self._create_user(**extra_fields)


class CustomAbstractBaseUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'
        ),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    data_joined = models.DateTimeField(_('data joined'), default=timezone.now)

    objects = CustomUserManager()

    class Meta:
        abstract = True
