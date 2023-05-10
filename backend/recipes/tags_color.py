from django.db import models


class TagsColor(models.TextChoices):
    CHOCOLATE = '#D2691E'
    GREEN = '#008000'
    AQUA = '#00FFFF'