import logging
import re

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate

from accounts.ldap_view import ad_instance
from accounts.libs.con_ldap import AD
from accounts.models import LdapServer
from accounts.views import web_logout
from common.lib import rsa_decrypt

logger = logging.getLogger('sso')


@login_required
def user_profile(request):
    return render(request, 'user/user_profile.html', locals())


@login_required
def change_password(request):
    """
    ldap ding local
    :param request:
    :return:
    """
    template = 'user/change_password.html'
    error = ''
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        repeat_password = request.POST.get('repeat_password')

        # 区分登录类型
        if request.user.login_info.source == 'local':
            # 校验旧密码是否正确
            user = authenticate(username=request.user.username, password=old_password)
            if user is None:
                return render(request, template, {"error": {"message": '旧密码错误'}})

            # 校验新旧是否一致
            if old_password == new_password:
                return render(request, template, {"error": {"message": '新密码不能和旧密码相同'}})

            # 校验密码复杂度
            pattern = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[\s\S]{8,32}$")
            if pattern.match(new_password) is None:
                return render(request, template, {"error": {"message": '新密码必须8-32个字符，至少包含1个大写字母，1个小写字母和1个数字'}})

            # 校验是否一致
            if new_password != repeat_password:
                return render(request, template, {"error": {"message": '两次输入密码必须一致'}})

            # 保存并返回是否成功
            try:
                request.user.set_password(new_password)
                request.user.save()
                web_logout(request)
                return redirect("page_wait", content='修改密码成功')
            except Exception as e:
                logger.error(e)
                return render(request, template, {"error": {"message": '修改密码内部错误'}})
        elif request.user.login_info.source == 'ldap':
            # 校验旧密码是否正确
            l_s = LdapServer.objects.get(id=request.user.login_info.ldap_server)
            try:
                ad = AD(host=l_s.host, port=l_s.port, user=l_s.user, password=rsa_decrypt(l_s.password),
                        base_dn=l_s.ldap_base_dn)
            except Exception as e:
                logger.error(e)
                return False, '认证服务器连接失败'
            check_status, user_info = ad.check_password(username=request.user.username, password=old_password)
            if not check_status:
                return render(request, template, {"error": {"message": '旧密码错误'}})

            # 校验新旧是否一致
            if old_password == new_password:
                return render(request, template, {"error": {"message": '新密码不能和旧密码相同'}})

            # 校验密码复杂度
            pattern = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[\s\S]{8,32}$")
            if pattern.match(new_password) is None:
                return render(request, template, {"error": {"message": '新密码必须8-32个字符，至少包含1个大写字母，1个小写字母和1个数字'}})

            # 校验是否一致
            if new_password != repeat_password:
                return render(request, template, {"error": {"message": '两次输入密码必须一致'}})

            # 保存并返回是否成功
            ad, group, people = ad_instance(request.user.login_info.ldap_server)
            all_user = ad.get_user_list()
            this_dn = ''
            for i in all_user:
                if 'mail' in i['attributes']:
                    if request.user.email in i['attributes']['mail']:
                        this_dn = i['dn']
                        break
            if this_dn == '':
                return render(request, template, {"error": {"message": 'ldap用户校验失败'}})
            status, msg = ad.modify_password(this_dn, new_password)
            if status:
                web_logout(request)
                return redirect("page_wait", content='修改密码成功')
            else:
                return render(request, template, {"error": {"message": '修改密码内部错误'}})

    return render(request, template, locals())

