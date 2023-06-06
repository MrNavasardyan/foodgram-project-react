from django.contrib import admin

from django.contrib import admin

from .models import CustomUser, Follow


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'is_superuser',
    )
    list_filter = ('username', 'email', 'is_superuser')
    search_fields = (
        'username',
        'email',
        'first_name',
        'last_name',
    )
    fieldsets = (
        (
            None,
            {
                'fields': (
                    'username',
                    'email',
                    'first_name',
                    'last_name',
                    'password',
                )
            },
        ),
        ('Permission role', {'fields': ('is_superuser',)}),
    )


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
