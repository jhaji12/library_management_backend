from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from .models import Student, Book, Faculty, Issue, User

class CustomUserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = get_user_model()
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'school')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
        ('School Info', {'fields': ('school',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'school'),
        }),
    )
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

admin.site.register(Student)
admin.site.register(Book)
admin.site.register(Faculty)
admin.site.register(Issue)
admin.site.register(User, CustomUserAdmin)
