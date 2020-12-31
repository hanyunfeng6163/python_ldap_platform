"""python_ldap_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from accounts.cas_view import ServiceValidateView
from accounts.dintalk_view import ding_callback
from dashboard.views import index, doc, test
from accounts import views

urlpatterns = [
    # 引入urls
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('website/', include('accounts.urls2')),
    path('personal/', include('accounts.urls3')),

    # 基础url
    path('', index),
    path('test/', test),
    path('ding_callback/', ding_callback),
    path('doc/<str:name>/', doc),

    # 自定义cas url
    path('login/', views.web_login, name='login'),
    path('logout/', views.web_logout, name='logout'),
    path('verify/', views.ticket_check, name='verify'),
    path('login_status/<str:web_tag>/<str:username>/<str:session_tag>/', views.login_status, name='login_status'),

    # cas 这里只是实现部分简单的协议，可以满足django-cas-ng使用 v3 ；
    # 接入配置可参考templates/doc/django_cas_ng_接入.md
    path('p3/serviceValidate/', ServiceValidateView.as_view(), name='cas_p3_service_validate'),
]
