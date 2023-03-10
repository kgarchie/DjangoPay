from django import forms
from .models import Transaction, User


# create a send money form
class SendMoneyForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['money_to', 'amount']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(SendMoneyForm, self).__init__(*args, **kwargs)
        self.fields['money_to'].queryset = User.objects.exclude(id=self.user.id)


# create a register form
class RegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()


# create a login form
class LoginForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget = forms.PasswordInput()
