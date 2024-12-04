from django.contrib import admin
from .models import bots, Botcategory

# Register your models here.
admin.site.register(bots)
admin.site.register(Botcategory)