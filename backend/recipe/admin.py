from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe

from .models import (
    Ingredients, Recipe,
    RecipeIngredient, Tag, Favorite, ShoppingCart
)

User = get_user_model()


@admin.register(Ingredients)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    list_display_links = ('name',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    search_fields = ('name', 'slug')
    list_display_links = ('name',)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'favorites_amount', 'get_img')
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    list_display_links = ('name',)
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('favorites_amount',)
    filter_horizontal = ('tags',)

    @admin.display(description='Добавлено в избранное')
    def favorites_amount(self, obj):
        return obj.favorites.count()

    @admin.display(description='Изображение')
    def get_img(self, obj):
        if obj.image:
            return mark_safe(f"<img src='{obj.image.url}' width=50>")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
