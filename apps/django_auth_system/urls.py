from django.urls import include, path

from django_auth_system.views import UserViewSet, experement, experiment_two
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('users', UserViewSet)

urlpatterns = [
    # path('', include('rest_social_auth.urls_session')),
    # path('', include('rest_social_auth.urls_jwt_pair')),
    path('auth/', include('rest_framework_social_oauth2.urls')),
    path('login/', experement),
    path('try/', experiment_two),
]

urlpatterns += router.urls
