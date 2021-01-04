from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import CreateView, UpdateView, ListView

from accounts.forms import RoleForm, UserForm, DomainuthorizedListForm, LdapServerForm
from accounts.libs.common import IsAdminMixin
from accounts.models import User, DomainuthorizedList, Role, WebAuthorizationRecord, LdapServer


class UserListView(LoginRequiredMixin, IsAdminMixin, ListView):
    model = User


class LdapServerListView(LoginRequiredMixin, IsAdminMixin, ListView):
    model = LdapServer


class LdapServerCreateView(LoginRequiredMixin, CreateView):
    model = LdapServer
    form_class = LdapServerForm
    success_url = '/accounts/ldapserver/list/'
    template_name = 'accounts/ldapserver_form.html'


class LdapServerUpdateView(LoginRequiredMixin, UpdateView):
    model = LdapServer
    form_class = LdapServerForm
    success_url = '/accounts/ldapserver/list/'
    template_name = 'accounts/ldapserver_form_update.html'


def ldapserver_detail(request, pk):
    this_object = LdapServer.objects.get(pk=pk)
    return render(request, 'accounts/ldapserver_detail.html', locals())


class RoleListView(LoginRequiredMixin, ListView):
    model = Role


class DomainuthorizedListListView(LoginRequiredMixin, ListView):
    model = DomainuthorizedList


class WebAuthorizationRecordListView(LoginRequiredMixin, ListView):
    model = WebAuthorizationRecord
    paginate_by = 12

    def get_queryset(self):
        new_context = WebAuthorizationRecord.objects.all().order_by('-id')
        return new_context
        # filter_val = self.request.GET.get('filter', 'give-default-value')
        # order = self.request.GET.get('orderby', 'give-default-value')
        # new_context = Update.objects.filter(
        #     state=filter_val,
        # ).order_by(order)
        # return new_context


@login_required
def role_delete(request, pk):
    status = 1
    try:
        sg = Role.objects.get(pk=pk)
        sg.delete()
        status = 0
    except Exception as e:
        pass
    return JsonResponse({'status': status})


class RoleCreateView(LoginRequiredMixin, CreateView):
    model = Role
    form_class = RoleForm
    success_url = '/accounts/role/list/'
    template_name = 'accounts/role_form.html'


class RoleUpdateView(LoginRequiredMixin, UpdateView):
    model = Role
    form_class = RoleForm
    success_url = '/accounts/role/list/'
    template_name = 'accounts/role_form_update.html'


@login_required
def user_delete(request, pk):
    status = 1
    try:
        sg = User.objects.get(pk=pk)
        sg.delete()
        status = 0
    except Exception as e:
        pass
    return JsonResponse({'status': status})


class UserCreateView(LoginRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    success_url = '/accounts/user/list/'
    template_name = 'accounts/user_form.html'


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    success_url = '/accounts/user/list/'
    template_name = 'accounts/user_form_update.html'

    def post(self, request, **kwargs):
        request.POST = request.POST.copy()
        # print(request.POST.getlist('roles'))
        # 开发和测试角色，全部更新jenkins的权限
        # 开发角色分配Yearing角色权限
        # 开发角色创建阿里云账号，并授权部分只读权限
        return super(UserUpdateView, self).post(request, **kwargs)


class DomainuthorizedListCreateView(LoginRequiredMixin, CreateView):
    model = DomainuthorizedList
    form_class = DomainuthorizedListForm
    success_url = '/website/domainthorized/list/'
    template_name = 'accounts/domainthorized_form.html'


class DomainuthorizedListUpdateView(LoginRequiredMixin, UpdateView):
    model = DomainuthorizedList
    form_class = DomainuthorizedListForm
    success_url = '/website/domainthorized/list/'
    template_name = 'accounts/domainthorized_form_update.html'


@login_required
def domainthorized_delete(request, pk):
    status = 1
    try:
        sg = DomainuthorizedList.objects.get(pk=pk)
        sg.delete()
        status = 0
    except Exception as e:
        pass
    return JsonResponse({'status': status})


@login_required
def ldapserver_delete(request, pk):
    status = 1
    try:
        sg = LdapServer.objects.get(pk=pk)
        sg.delete()
        status = 0
    except Exception as e:
        pass
    return JsonResponse({'status': status})