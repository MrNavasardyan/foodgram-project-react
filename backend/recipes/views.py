from django.shortcuts import render
from rest_framework import viewsets
from recipes.models import Recipe


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
