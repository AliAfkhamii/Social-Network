from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django.utils.translation import gettext_lazy as _
from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label=_('password'), required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, label=_('confirm password'), required=True)

    class Meta:
        model = User
        fields = ('email', 'username',)

    def clean(self):
        data = self.cleaned_data
        if data['password'] != data['password2']:
            raise forms.ValidationError(_("password won't match"))
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data.get('password'))
        if commit:
            user.save()
        return user


class AdministrationUserChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField(help_text=("Raw passwords are not stored, so there is no way to see "
                                                    "this user's password, but you can change the password "
                                                    "using <a href=\"../password/\">this form</a>.")
                                         )
    class Meta:
        model = User
        fields = '__all__'

    def clean_password(self):
        return self.initial.get('password')
