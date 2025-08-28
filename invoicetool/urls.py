from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
   path('add/', views.add_client, name='add_client'),
    path('', views.client_list, name='client_list'),
    path("invoices/", include("invoices.urls")),
    # etc...
]

