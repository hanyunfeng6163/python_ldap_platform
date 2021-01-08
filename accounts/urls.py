from django.urls import path

from accounts.fronts import UserListView, RoleListView, LdapServerListView, role_delete, RoleCreateView, RoleUpdateView, \
    UserUpdateView, UserCreateView, user_delete, LdapServerCreateView, ldapserver_delete, LdapServerUpdateView, \
    ldapserver_detail, ldap_user_add_to_local
from accounts.ldap_view import ldap_tree, ldap_all_user, ldap_group_user, ldap_group_edit, ldap_group_form_tree, \
    ldap_group_add, ldap_user_add, ldap_user_form_tree, ldap_user_edit, ldap_user_delete, send_forget_password_email, \
    email_reset_password, page_wait, ldap_user_reset_password

urlpatterns = [
    path('ldapserver/list/', LdapServerListView.as_view(), name='ldapserver_list'),
    path('ldapserver/add/', LdapServerCreateView.as_view(), name='ldapserver_add'),
    path('ldapserver/delete/<int:pk>/', ldapserver_delete, name='ldapserver_delete'),
    path('ldapserver/update/<int:pk>/', LdapServerUpdateView.as_view(), name='ldapserver_update'),
    path('ldapserver/detail/<int:pk>/', ldapserver_detail, name='ldapserver_detail'),

    path('role/list/', RoleListView.as_view(), name='role_list'),
    path('role/delete/<int:pk>/', role_delete, name='role_delete'),
    path('role/add/', RoleCreateView.as_view(), name='role_add'),
    path('role/update/<int:pk>/', RoleUpdateView.as_view(), name='role_update'),

    path('user/list/', UserListView.as_view(), name='user_list'),
    path('user/delete/<int:pk>/', user_delete, name='user_delete'),
    path('user/add/', UserCreateView.as_view(), name='user_add'),
    path('user/update/<int:pk>', UserUpdateView.as_view(), name='user_update'),
    path('user/ldap_user_add_to_local/', ldap_user_add_to_local, name='ldap_user_add_to_local'),

    # ldap detail页面
    path('ldap/ldap_tree/<int:pk>/', ldap_tree, name='ldap_tree'),
    path('ldap/ldap_all_user/<int:pk>/', ldap_all_user, name='ldap_all_user'),
    path('ldap/ldap_group_user/<int:pk>/<str:group_dn>/', ldap_group_user, name='ldap_group_user'),
    path('ldap/ldap_group_edit/<int:pk>/<str:parent_dn>/<str:group_dn>/', ldap_group_edit, name='ldap_group_edit'),
    path('ldap/ldap_group_add/<int:pk>/<str:parent_dn>/', ldap_group_add, name='ldap_group_add'),
    path('ldap/ldap_user_add/<int:pk>/<str:user_parent_dn>/', ldap_user_add, name='ldap_user_add'),
    path('ldap/ldap_user_edit/<int:pk>/<str:cn>/', ldap_user_edit, name='ldap_user_edit'),
    path('ldap/ldap_user_delete/<int:pk>/<str:cn>/', ldap_user_delete, name='ldap_user_delete'),
    path('ldap/ldap_user_reset_password/<int:pk>/<str:cn>/', ldap_user_reset_password, name='ldap_user_reset_password'),
    path('ldap/ldap_group_form_tree/<int:pk>/<str:group_dn>/', ldap_group_form_tree, name='ldap_group_form_tree'),
    path('ldap/ldap_user_form_tree/<int:pk>/', ldap_user_form_tree, name='ldap_user_form_tree'),
    # 忘记ldap密码
    path('ldap/send_forget_password_email/<int:pk>/', send_forget_password_email, name='send_forget_password_email'),
    path('ldap/page_wait/<str:content>/', page_wait, name='page_wait'),
    path('ldap/email_reset_password/<str:token>/', email_reset_password, name='email_reset_password'),

]
