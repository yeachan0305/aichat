from django.contrib import admin
from .models import postdb, Category, Comment

# Register your models here.
admin.site.register(postdb)
admin.site.register(Category)
admin.site.register(Comment)