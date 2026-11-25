from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Article, Category, Comment, CustomUser, EmailConfirmation


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("username", "email", "is_active", "is_staff")
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Email", {"fields": ("email",)}),
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "created_at", "is_published")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "summary", "content")


admin.site.register(Category)
admin.site.register(Comment)
@admin.register(EmailConfirmation)
class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "is_confirmed")
    list_filter = ("is_confirmed", "created_at")
