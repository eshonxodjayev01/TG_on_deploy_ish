from django import forms
from django.contrib.auth.models import User

from burger.models import  Order


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={'placeholder': "Your name", }
        )
    )
    email = forms.EmailField(
        widget=forms.TextInput(
            attrs={'placeholder': "Your e-mail", }
        )
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'placeholder': 'Your message', }
        )
    )


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        exclude = ('paid',)

        widgets = {
            'address': forms.Textarea(attrs={'row': 5, 'col': 8}),
        }

class StripePaymentForm(forms.Form):
    selectedCard = forms.CharField()
