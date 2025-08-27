from django import forms
from .models import Client, Item, Invoice



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['name', 'email', 'phone', 'address']

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price']

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['client', 'items', 'due_date', 'is_paid']
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'}),
            'items': forms.CheckboxSelectMultiple(),  # multiple items selection
        }


