from django.contrib import admin

from .models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'first_name', 'last_name',
                    'email', 'password')
    list_editable = ('password',)
    list_filter = ('username', 'email',)
    search_fields = ('username', 'email',)
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
