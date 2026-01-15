import re
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator

from stockapp.models.cassandra_db import Users
from stockapp.models.crud_operations import read_record

class RegisterForm(forms.Form):
    email=forms.EmailField()
    password=forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password=forms.CharField(widget=forms.PasswordInput, required=True)
      
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email không được để trống.")
        try:
            EmailValidator()(email)
        except ValidationError:
            raise ValidationError("Email không hợp lệ.")
        conditions = {'email': email}
        records = read_record(Users, **conditions)
        if records:
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
    email=forms.EmailField()
    name=forms.CharField(required=True)
    phonenumber=forms.CharField(required=True)

    def __init__(self, *args, **kwargs):
        initial_email = kwargs.pop('initial_email', None)
        super().__init__(*args, **kwargs)
        if initial_email:
            self.fields['email'].initial = initial_email
            self.fields['email'].disabled = True 

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
        email = cleaned_data.get('email')
        name = cleaned_data.get('name')
        phonenumber = cleaned_data.get('phonenumber')

        return cleaned_data
