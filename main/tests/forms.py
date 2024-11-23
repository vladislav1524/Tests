from django import forms
from django.core.exceptions import ValidationError
from allauth.account.forms import SignupForm


# auth
class CustomSignupForm(SignupForm):
    username = forms.CharField(max_length=150, label='Ваше имя')

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if not username:
            raise ValidationError("Введите ваше имя.")

        return username
    
    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.username = self.cleaned_data['username']
        user.save()
        return user
    

class EmailForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=254)
