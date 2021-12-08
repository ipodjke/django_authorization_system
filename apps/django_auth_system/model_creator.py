from typing import Dict, Optional

from django.contrib.auth.models import AbstractUser
from django.db import models

from django_auth_system.abstract_user_model import CustomAbstractBaseUser
from django_auth_system.apps import UsersConfig
from django_auth_system.conf import settings
from django_auth_system.validators import SchemaValidator


class UserModelCreator:
    def __init__(self) -> None:
        self._validator = SchemaValidator()
        self._field_creator = FieldCreator()
        self._meta_creator = MetaModelCreator()

    def create_model(self):
        if self._check_is_default_django_model():
            return AbstractUser

        self._validator.validate_schema()

        return type('CustomUser', (CustomAbstractBaseUser,), self._get_attrs())

    def _check_is_default_django_model(self, schema: Optional[Dict] = None) -> bool:
        if schema is None:
            from django.conf import settings
            schema = getattr(settings, 'DJANGO_AUTH_SYSTEM', None)
        return schema is None or schema.get('USER_MODEL_SCHEMA') is None

    def _get_attrs(self) -> Dict:
        return {
            **self._create_key_implementation_details(),
            **self._get_model_meta(),
            **self._get_fields()
        }

    def _create_key_implementation_details(self) -> Dict:
        user_schema = settings.USER_MODEL_SCHEMA
        return {
            'USERNAME_FIELD': user_schema['USERNAME_FIELD'],
            'REQUIRED_FIELDS': user_schema['REQUIRED_FIELDS'],
            '__module__': UsersConfig.name,
        }

    def _get_model_meta(self):
        return self._meta_creator.create_meta_class(
            settings.USER_MODEL_SCHEMA.get('META')
        )

    def _get_fields(self) -> Dict:
        return self._field_creator.create_fields(
            settings.USER_MODEL_SCHEMA.get('FIELDS')
        )


class FieldCreator:
    def create_fields(self, fields: Dict) -> Dict:
        return {name: getattr(models, field['field_type'])(**field['attrs'])
                for name, field in fields.items()}


class MetaModelCreator:
    def create_meta_class(self, meta_data: Dict) -> Dict:
        class Meta:
            pass
        self._change_abstract_param(meta_data)
        # meta = self._merge_default_and_custom_meta(meta_data)
        for key, value in meta_data.items():
            setattr(Meta, key, value)

        return {'Meta': Meta}

    def _change_abstract_param(self, meta_data: Dict) -> None:
        if ('abstract' in meta_data.keys()
                and meta_data['abstract'] is False):
            meta_data['abstract'] = True

    # def _merge_default_and_custom_meta(self, meta_data: Dict) -> Dict:
    #     return {**settings.DEFAULT_META_FIELDS, **meta_data}
