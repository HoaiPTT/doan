import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from stockapp.models.mongo_db import Users

class RegisterForm(forms.ModelForm):
    confirm_password=forms.CharField(widget=forms.PasswordInput, required=True)
    class Meta:
        model=Users
        fields = ['email', 'password']
        widgets = {
            'password': forms.PasswordInput(),
        }
      
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email không được để trống.")
        try:
            EmailValidator()(email)
        except ValidationError:
            raise ValidationError("Email không hợp lệ.")
        if Users.objects.filter(email=email).exists():
            raise ValidationError("Email đã tồn tại.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not re.fullmatch(r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[\W_]).{6,}$', password):
            raise ValidationError("Mật khẩu phải có ít nhất 6 ký tự, bao gồm chữ cái, chữ số và ký tự đặc biệt.")
        return password
    
    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password != confirm_password:
            raise ValidationError("Mật khẩu và xác nhận mật khẩu không khớp.")
        return confirm_password
    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        return cleaned_data

class UserInfoForm(forms.Form):
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    name = forms.CharField()
    phonenumber = forms.CharField()

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if not name:
            raise ValidationError("Vui lòng nhập tên của bạn.")
        return name
    def clean_phonenumber(self):
        phonenumber = self.cleaned_data.get('phonenumber')
        if not re.fullmatch(r'0\d{9}', phonenumber):
            raise ValidationError("Vui lòng nhập đúng số điện thoại.")
        return phonenumber
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        phonenumber = cleaned_data.get('phonenumber')

        return cleaned_data
