from django.urls import path, include
from rest_framework.routers import DefaultRouter

import users.views as views

app_name = 'users'

router = DefaultRouter()
router.register('accounting', views.UserAccounting, basename='accounting')

urlpatterns = [
    path('api/', include(router.urls)),
]
