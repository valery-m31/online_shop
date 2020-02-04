from django.forms import ModelForm, Textarea

from .models import Address


class CreateAddressForm(ModelForm):
    class Meta:
        model = Address
        fields = [
            'first_name',
            'last_name',
            'country',
            'city',
            'zip_code',
            'home_address',
            'phone',
            'email',
            ]
        widgets = {
            'home_address': Textarea(attrs={
                'rows': 1,
                'cols': 37,
                'placeholder': 'Street building flat'
                }),
            'first_name': Textarea(attrs={
                'rows': 1,
                'cols': 37,
                'placeholder': 'Petya'
                }),
            'last_name': Textarea(attrs={
                'rows': 1,
                'cols': 37,
                'placeholder': 'Petrov'
                }),
            'city': Textarea(attrs={
                'rows': 1,
                'cols': 37,
                'placeholder': 'Moscow'
                }),
            'zip_code': Textarea(attrs={
                'rows': 1,
                'cols': 37,
                'placeholder': '123456'
                }),
            'phone': Textarea(attrs={
                'rows': 1,
                'cols': 37,
                'placeholder': '+123456789'
                }),
            'email': Textarea(attrs={
                'rows': 1,
                'cols': 37,
                'placeholder': 'youremail@gmail.com'
                })
            }
