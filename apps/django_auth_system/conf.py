from django.conf import settings as django_settings
from django.test.signals import setting_changed
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

DJ_AUTH_SYSTEM_SETTING_NAMESPACE = 'DJANGO_AUTH_SYSTEM'


class ObjDict(dict):
    def __getattribute__(self, item):
        try:
            val = self[item]
            if isinstance(val, str):
                val = import_string(val)
            elif isinstance(val, (list, tuple)):
                val = [import_string(v) if isinstance(v, str) else v for v in val]
            self[item] = val
        except KeyError:
            val = super(ObjDict, self).__getattribute__(item)

        return val


default_settings = {
    'SEND_ACTIVATION_EMAIL': False,
    'SEND_CONFIRMATION_EMAIL': False,
    'USER_CREATE_PASSWORD_RETYPE': False,
    'SET_PASSWORD_RETYPE': False,
    'PASSWORD_RESET_CONFIRM_RETYPE': False,
    'SET_USERNAME_RETYPE': False,
    'USERNAME_RESET_CONFIRM_RETYPE': False,
    'PASSWORD_RESET_SHOW_EMAIL_NOT_FOUND': False,
    'USERNAME_RESET_SHOW_EMAIL_NOT_FOUND': False,
    'PASSWORD_CHANGED_EMAIL_CONFIRMATION': False,
    'USERNAME_CHANGED_EMAIL_CONFIRMATION': False,
    'SERIALIZERS': ObjDict(
        {
            'activation': 'django_auth_system.serializers.ActivationSerializer',
            'password_reset': 'django_auth_system.serializers.SendEmailResetSerializer',
            'password_reset_confirm': 'django_auth_system.serializers.PasswordResetConfirmSerializer',
            'password_reset_confirm_retype': 'django_auth_system.serializers.PasswordResetConfirmRetypeSerializer',
            'set_password': 'django_auth_system.serializers.SetPasswordSerializer',
            'set_password_retype': 'django_auth_system.serializers.SetPasswordRetypeSerializer',
            'set_username': 'django_auth_system.serializers.SetUsernameSerializer',
            'set_username_retype': 'django_auth_system.serializers.SetUsernameRetypeSerializer',
            'username_reset': 'django_auth_system.serializers.SendEmailResetSerializer',
            'username_reset_confirm': 'django_auth_system.serializers.UsernameResetConfirmSerializer',
            'username_reset_confirm_retype': 'django_auth_system.serializers.UsernameResetConfirmRetypeSerializer',
            'user_create': 'django_auth_system.serializers.UserCreateSerializer',
            'user_create_password_retype': 'django_auth_system.serializers.UserCreatePasswordRetypeSerializer',
            'user_delete': 'django_auth_system.serializers.UserDeleteSerializer',
            'user': 'django_auth_system.serializers.UserSerializer',
            'current_user': 'django_auth_system.serializers.UserSerializer',
        }
    ),
    'EMAIL': ObjDict(
        {
            'activation': 'django_auth_system.email.ActivationEmail',
            'confirmation': 'django_auth_system.email.ConfirmationEmail',
            'password_reset': 'django_auth_system.email.PasswordResetEmail',
            'password_changed_confirmation': 'django_auth_system.email.PasswordChangedConfirmationEmail',
            'username_changed_confirmation': 'django_auth_system.email.UsernameChangedConfirmationEmail',
            'username_reset': 'django_auth_system.email.UsernameResetEmail',
        }
    ),
    'CONSTANTS': ObjDict({'messages': 'django_auth_system.constants.Messages'}),
    'LOGOUT_ON_PASSWORD_CHANGE': False,
    'HIDE_USERS': True,
    'PERMISSIONS': ObjDict(
        {
            'activation': ['rest_framework.permissions.AllowAny'],
            'password_reset': ['rest_framework.permissions.AllowAny'],
            'password_reset_confirm': ['rest_framework.permissions.AllowAny'],
            'set_password': ['django_auth_system.permissions.CurrentUserOrAdmin'],
            'username_reset': ['rest_framework.permissions.AllowAny'],
            'username_reset_confirm': ['rest_framework.permissions.AllowAny'],
            'set_username': ['django_auth_system.permissions.CurrentUserOrAdmin'],
            'user_create': ['rest_framework.permissions.AllowAny'],
            'user_delete': ['django_auth_system.permissions.CurrentUserOrAdmin'],
            'user': ['django_auth_system.permissions.CurrentUserOrAdmin'],
            'user_list': ['django_auth_system.permissions.CurrentUserOrAdmin'],
        }
    ),
    'REQUIRED_SCHEMA_FIELDS': ['USERNAME_FIELD', 'REQUIRED_FIELDS', 'FIELDS'],
    'USER_MODEL_SCHEMA': {
        'META': {
            'abstract': True,
            'verbose_name': _('User'),
            'verbose_name_plural': _('Users'),
        }
    },
}

SETTINGS_TO_IMPORT = []


class Settings:
    def __init__(self, default_settings, explicit_overriden_settings: dict = None):
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}

        overriden_settings = (
            getattr(django_settings, DJ_AUTH_SYSTEM_SETTING_NAMESPACE, {})
            or explicit_overriden_settings
        )

        self._load_default_settings()
        self._override_settings(overriden_settings)
        self._init_settings_to_import()

    def _load_default_settings(self):
        for setting_name, setting_value in default_settings.items():
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

    def _override_settings(self, overriden_settings: dict):
        for setting_name, setting_value in overriden_settings.items():
            value = setting_value
            if isinstance(setting_value, dict):
                value = getattr(self, setting_name, {})
                value.update(ObjDict(setting_value))
            setattr(self, setting_name, value)

    def _init_settings_to_import(self):
        for setting_name in SETTINGS_TO_IMPORT:
            value = getattr(self, setting_name)
            if isinstance(value, str):
                setattr(self, setting_name, import_string(value))


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(default_settings, explicit_overriden_settings)


settings = LazySettings()


def reload_auth_system_settings(*args, **kwargs):
    global settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == DJ_AUTH_SYSTEM_SETTING_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_auth_system_settings)
