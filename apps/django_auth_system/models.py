# from django.utils.translation import gettext_lazy as _

from django_auth_system.model_creator import UserModelCreator

user = UserModelCreator().create_model()


class User(user):
    class Meta(user.Meta):
        abstract = False
