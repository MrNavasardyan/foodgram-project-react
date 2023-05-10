from django.db import models


class TagsColor(models.Choices):
    CHOCOLATE = '#D2691E'
    GREEN = '#008000'
    AQUA = '#00FFFF'

    TAGS = [
        (CHOCOLATE, 'Завтрак'),
        (GREEN,'Обед'),
        (AQUA, 'Ужин')
    ]