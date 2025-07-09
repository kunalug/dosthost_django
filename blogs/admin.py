# admin.py
from django.contrib import admin
from .models import Blog, Categories, Tag, Comment

# Categories
@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# Tags
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

# Blogs
@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'display_categories', 'created_at', 'image')
    search_fields = ('title', 'author__username')
    list_filter = ('created_at', 'categories', 'tags')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('tags', 'categories')

    def display_categories(self, obj):
        return ", ".join([cat.name for cat in obj.categories.all()])
    display_categories.short_description = 'Categories'

# Comments
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog', 'author', 'created_at', 'approved')
    search_fields = ('author', 'content')
    list_filter = ('approved', 'created_at')
    readonly_fields = ('created_at',)