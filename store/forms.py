from django import forms
from .models import Order


class ContactForm(forms.Form):
    name = forms.CharField(label="Ім’я", max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    message = forms.CharField(label="Повідомлення", widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['name', 'phone', 'address']
