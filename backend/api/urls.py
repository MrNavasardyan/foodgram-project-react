from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter
from .views import RecipeViewSet, TagViewSet, IngredientViewSet, UserViewSet
from django.conf import settings
from django.conf.urls.static import static


router = DefaultRouter()
router.register('recipes', RecipeViewSet)
router.register('tags', TagViewSet)
router.register('ingredients', IngredientViewSet)
router.register('user', UserViewSet)


urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    re_path(r'auth/', include('djoser.urls.authtoken'))
]

# if settings.DEBUG:
#     urlpatterns += static(
#         settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
#     )