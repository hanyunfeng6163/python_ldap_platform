## ceshi
setting.py配置
```
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cas_ng',
]
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend',
)


CAS_SERVER_URL = 'http://127.0.0.1:8888'
# CAS 版本
CAS_VERSION = '3'
# 存入所有 CAS 服务端返回的 User 数据。
CAS_APPLY_ATTRIBUTES_TO_USER = True
```

url配置
```
path('accounts/login/', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
path('accounts/logout/', django_cas_ng.views.LogoutView.as_view(), name='cas_ng_logout'),
path('accounts/callback/', django_cas_ng.views.CallbackView.as_view(), name='cas_ng_proxy_callback'),
```