from django import forms

from accounts.models import Role, User, DomainuthorizedList, LdapServer


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('title', 'mark', 'external_permission')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control col-sm-4'}),
            'mark': forms.TextInput(attrs={'class': 'form-control col-sm-4'}),
            'external_permission': forms.SelectMultiple(attrs={'class': 'form-control demo2', 'size': '10', 'multiple': 'multiple'}),
        }


class LdapServerForm(forms.ModelForm):
    class Meta:
        model = LdapServer
        fields = '__all__'



class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username', 'nickname', 'email', 'phone', 'is_lock', 'is_active', 'roles', 'is_superuser')
        labels = {
            'username': '用户名',
            'nickname': '中文名',
            'email': '邮箱',
            'phone': '电话',
            'is_lock': '是否锁定',
            'is_active': '是否激活',
            'is_superuser': '管理员',
        }


class DomainuthorizedListForm(forms.ModelForm):
    class Meta:
        model = DomainuthorizedList
        fields = ('name', 'mark', 'domain_name', 'logout_api_url')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control col-sm-4'}),
            'mark': forms.TextInput(attrs={'class': 'form-control col-sm-4'}),
            'domain_name': forms.TextInput(attrs={'class': 'form-control col-sm-4'}),
            'logout_api_url': forms.TextInput(attrs={'class': 'form-control col-sm-4'}),
        }
