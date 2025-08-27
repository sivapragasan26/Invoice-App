from django.contrib import admin
from .models import Client, Item, Invoice

admin.site.register(Client)
admin.site.register(Item)
admin.site.register(Invoice)

