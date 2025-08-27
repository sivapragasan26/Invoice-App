from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Client URLs
    path('add_client/', views.add_client, name='add_client'),
    path('clients/', views.client_list, name='client_list'),
    path('edit_client/<int:client_id>/', views.edit_client, name='edit_client'),
    path('delete_client/<int:client_id>/', views.delete_client, name='delete_client'),

    # Item URLs
    path('add_item/', views.add_item, name='add_item'),
    path('items/', views.item_list, name='item_list'),
    path('edit_item/<int:item_id>/', views.edit_item, name='edit_item'),
    path('delete_item/<int:item_id>/', views.delete_item, name='delete_item'),

    # Invoice URLs
    path('add_invoice/', views.add_invoice, name='add_invoice'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoice/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),  # ✅ important
    # Invoice edit
    path('edit_invoice/<int:invoice_id>/', views.edit_invoice, name='edit_invoice'),
    path('delete_invoice/<int:invoice_id>/', views.delete_invoice, name='delete_invoice'),

    # Authentication (if applicable)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('add_invoice/', views.add_invoice, name='add_invoice'),
    path('send_invoice/<int:invoice_id>/', views.send_invoice_email, name='send_invoice'),

]
