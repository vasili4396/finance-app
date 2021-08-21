from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class SexTypes(models.IntegerChoices):
        FEMALE = 1, 'Женский'
        MALE = 2, 'Мужской'

    birthday = models.DateField(verbose_name='Дата рождения', blank=True, null=True)
    sex = models.SmallIntegerField(choices=SexTypes.choices, verbose_name='пол', null=True, blank=True)
