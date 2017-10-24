from django import forms
from django.contrib.auth.models import User



class login_form (forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','password']

    def __init__(self,*args,**kwargs):
        super(login_form, self).__init__(*args,*kwargs)
        self.fields['password'].widget = forms.PasswordInput()