import json
import logging
import re

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.clickjacking import xframe_options_exempt

from accounts.libs.con_ldap import AD, group_dn_magic, group_dn_magic_re
from accounts.models import LdapUserEmailVerifyRecord, LdapServer
from common.lib import random_str, rsa_decrypt
from django.utils import timezone

logger = logging.getLogger('sso')


def ad_instance(pk):
    try:
        l_s = LdapServer.objects.get(pk=pk)
        ldap_group_dn = "{group_dn},{base_dn}".format(group_dn=l_s.ldap_group_dn, base_dn=l_s.ldap_base_dn)
        ldap_user_dn = "{user_dn},{base_dn}".format(user_dn=l_s.ldap_user_dn, base_dn=l_s.ldap_base_dn)
        return AD(host=l_s.host, port=l_s.port, user=l_s.user,
                  password=rsa_decrypt(l_s.password), base_dn=l_s.ldap_base_dn,
                  ldap_user_object_class=l_s.ldap_user_object_class,
                  ldap_group_object_class=l_s.ldap_group_object_class), ldap_group_dn, ldap_user_dn
    except Exception as e:
        logger.error(e)
        return None


@login_required
def ldap_tree(request, pk):
    ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
    return JsonResponse(ad.get_group_tree_json(), safe=False)


@login_required
def ldap_all_user(request, pk):
    ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
    return JsonResponse(ad.get_user_list(), safe=False)


@login_required
def ldap_group_user(request, pk, group_dn):
    ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
    cns = group_dn_magic(group_dn, ldap_group_dn)
    return JsonResponse(ad.search_group_user_list(dn=cns), safe=False)


@login_required
@xframe_options_exempt
def ldap_group_edit(request, pk, parent_dn, group_dn):
    """
    编辑组
    :param request:
    :param parent_dn:
    :param group_dn:
    :param pk:
    :return:
    """
    # 切割主当前的组名用于前端展示
    old_group_dn = group_dn.split('-')[-1]

    if request.method == 'POST':
        ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)

        upper_group = request.POST['upper_group']
        # upper_group = request.POST.getlist('upper_group')
        # 后台传入的问题，到底是个对象还是list呢
        group_name = request.POST['group_name']
        logger.info('正在修改当前组的名称或上级组织[{old_group_dn}]->[{group_name}],[{parent_dn}]->[{upper_group}]'.format(
            upper_group=upper_group,
            group_name=group_name,
            parent_dn=parent_dn,
            old_group_dn=old_group_dn))

        cns = group_dn_magic(upper_group, ldap_group_dn)
        trans_new_dn = 'cn={group_name},{cns}'.format(group_name=group_name, cns=cns)
        trans_old_dn = group_dn_magic(group_dn, ldap_group_dn)

        if ad.update_group_name_or_upper(trans_old_dn, trans_new_dn):
            return JsonResponse({'status': 0})
        else:
            return JsonResponse({'status': 1})
    return render(request, 'ldap/ldap_group_edit.html', locals())


@login_required
def ldap_group_form_tree(request, pk, group_dn=''):
    ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
    return JsonResponse(ad.get_group_menu_tree_json(group_dn), safe=False)


@login_required
def ldap_user_form_tree(request, pk):
    ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
    return JsonResponse(ad.get_user_menu_tree_json(), safe=False)


@login_required
@xframe_options_exempt
def ldap_group_add(request, pk, parent_dn):
    """
    指定父节点创建一个组
    :param request:
    :param parent_dn:
    :return:
    """
    if request.method == 'POST':
        upper_group = request.POST['upper_group']
        group_name = request.POST['group_name']
        ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
        if upper_group == 'top':
            # 如果是顶级部门，直接将组名和Group后面拼接
            trans_new_dn = 'cn={group_name},{ldap_group_dn}'.format(group_name=group_name, ldap_group_dn=ldap_group_dn)
        else:
            # 如果不是顶级部门，先拼接处上级部门，然后组装到一起生成新的dn
            cns = group_dn_magic(upper_group, ldap_group_dn)
            trans_new_dn = 'cn={group_name},{cns}'.format(group_name=group_name, cns=cns)

        status, msg = ad.create_obj(dn=trans_new_dn, obj_type='ou',
                                    attr={'uniqueMember': 'cn=base,{ldap_user_dn}'.format(ldap_user_dn=ldap_user_dn)})
        if status:
            return JsonResponse({'status': 0})
        else:
            logger.error(msg)
            return JsonResponse({'status': 1})
    return render(request, 'ldap/ldap_group_add.html', locals())


@login_required
@xframe_options_exempt
def ldap_user_add(request, pk, user_parent_dn):
    # 添加用户，并指定组
    if request.method == 'POST':
        user_group = request.POST['user_group']  # ["-技术部","-技术部-运维部","-技术部-运维部-系统运维"]
        email_prefix = request.POST['email_prefix']
        email_suffix = request.POST['email_suffix']
        display_name = request.POST['display_name']
        phone = request.POST['phone']
        cn = request.POST['cn']
        ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
        mail = "{email_prefix}@{email_suffix}".format(email_prefix=email_prefix, email_suffix=email_suffix)
        attr = {}
        dn = "cn={cn},{ldap_user_dn}".format(cn=cn, ldap_user_dn=ldap_user_dn)
        attr['mail'] = mail
        attr['uid'] = cn
        attr['sn'] = cn  # sn 为姓，这里不规范
        if display_name != '':
            attr['displayName'] = display_name
        if phone != '':
            attr['telephoneNumber'] = phone
        # 随机一个密码
        new_password = random_str(randomlength=16)
        # 创建用户
        add_user_result = ad.create_obj(dn, "user", attr=attr, new_password=new_password)
        # 添加用户并判断成功与否
        if not add_user_result[0]:
            logger.error('用户创建失败{}'.format(add_user_result[1]))
            return JsonResponse({'status': 1, 'msg': add_user_result[1]['description']})

        # 添加到组
        try:
            for one_group in eval(user_group):
                cns = group_dn_magic(one_group, ldap_group_dn)
                ad.group_add_user(cns, attr={'uniqueMember': dn})
        except Exception as e:
            logger.error(e)
        return JsonResponse({'status': 0, 'pwd':new_password})
    return render(request, 'ldap/ldap_user_add.html', locals())


@login_required
@xframe_options_exempt
def ldap_user_edit(request, pk, cn):
    # 添加用户，并指定组
    ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)

    # 获取用户的具体信息返回
    status, user_info = ad.search_user_info(cn)
    if status:
        try:
            email_prefix = user_info['mail'][0].split('@')[0]  # 邮箱前缀
            email_suffix = user_info['mail'][0].split('@')[1]  # 邮箱后缀
        except Exception as e:
            logger.error(e)
            email_prefix = ''
            email_suffix = ''

        try:
            phone = user_info['telephoneNumber'][0]  # 手机号
        except Exception as e:
            logger.error(e)
            phone = ''

        try:
            display_name = user_info['displayName']  # 手机号
        except Exception as e:
            logger.error(e)
            display_name = ''
    # 获取当前用户的全部组，然后取出dn 拼装成 ['-产品中心', '-产品中心-前端产品'] 这样的列表返回
    group_info = ad.search_user_groups(cn)
    group_dn_list = []  # 所属部门，多个
    for group_dn in [x['dn'] for x in group_info]:
        group_dn_list.append(group_dn_magic_re(group_dn))

    if request.method == 'POST':
        user_group = request.POST['user_group']  # ["-技术部","-技术部-运维部","-技术部-运维部-系统运维"]
        email_prefix = request.POST['email_prefix']
        email_suffix = request.POST['email_suffix']
        display_name = request.POST['display_name']
        phone = request.POST['phone']
        new_cn = request.POST['cn']
        ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
        # 更新用户属性
        dn = "cn={cn},{ldap_user_dn}".format(cn=cn, ldap_user_dn=ldap_user_dn)
        new_dn = "cn={new_cn},{ldap_user_dn}".format(new_cn=new_cn, ldap_user_dn=ldap_user_dn)
        mail = "{email_prefix}@{email_suffix}".format(email_prefix=email_prefix, email_suffix=email_suffix)

        attr = {}
        attr['mail'] = mail
        attr['uid'] = new_cn
        attr['sn'] = new_cn  # sn 为姓，这里不规范
        if display_name != '':
            attr['displayName'] = display_name
        if phone != '':
            attr['telephoneNumber'] = phone

        add_user_result = ad.update_obj(dn, attr=attr)

        # 添加用户参数与否更新
        if not add_user_result:
            logger.error('用户修改失败{}'.format(add_user_result[1]))
            return JsonResponse({'status': 1, })

        # 是否修改名
        if new_cn != cn:
            ad.rename_obj(dn, 'cn={}'.format(new_cn))

        try:
            del_group = list(set(group_dn_list) - set(eval(user_group)))
            add_group = list(set(eval(user_group)) - set(group_dn_list))
        except Exception as e:
            del_group = []
            add_group = []
        # 如果有修改名 则先移除组
        if new_cn != cn:
            # 如果改名了，先将旧用户移除全部组，再把新用户添加全部组
            for old_del_group in group_dn_list:
                cns = group_dn_magic(old_del_group, ldap_group_dn)
                ad.group_del_user(cns, attr={'uniqueMember': dn})

            # 添加到组
            for one_add_group in eval(user_group):
                cns = group_dn_magic(one_add_group, ldap_group_dn)
                ad.group_add_user(cns, attr={'uniqueMember': new_dn})
        else:
            # 如果没改名，计算差，哪个是添加，哪个是删除
            # 添加到组
            for one_add_group in add_group:
                cns = group_dn_magic(one_add_group, ldap_group_dn)
                ad.group_add_user(cns, attr={'uniqueMember': dn})
            # 移除用户组
            for one_del_group in del_group:
                cns = group_dn_magic(one_del_group, ldap_group_dn)
                ad.group_del_user(cns, attr={'uniqueMember': dn})

        return JsonResponse({'status': 0})
    return render(request, 'ldap/ldap_user_edit.html', locals())


@login_required
def ldap_user_delete(request, pk, cn):
    ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
    # 获取当前用户的全部组，然后取出dn 拼装成 ['-产品中心', '-产品中心-前端产品'] 这样的列表返回
    group_info = ad.search_user_groups(cn)
    group_dn_list = []  # 所属部门，多个
    for group_dn in [x['dn'] for x in group_info]:
        group_dn_list.append(group_dn_magic_re(group_dn))
    dn = "cn={cn},{ldap_user_dn}".format(cn=cn, ldap_user_dn=ldap_user_dn)
    # 从对应的组里删除当前用户
    for old_del_group in group_dn_list:
        cns = group_dn_magic(old_del_group, ldap_group_dn)
        ad.group_del_user(cns, attr={'uniqueMember': dn})
    # 删除当前用户
    if ad.del_obj(dn):
        return JsonResponse({'status': 0})
    else:
        return JsonResponse({'status': 1})


@login_required
def ldap_user_reset_password(request, pk, cn):
    ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
    dn = "cn={cn},{ldap_user_dn}".format(cn=cn, ldap_user_dn=ldap_user_dn)
    newpassword = random_str(randomlength=16)
    status, msg = ad.modify_password(dn=dn, newpassword=newpassword)
    if status:
        return JsonResponse({'status': 0, 'msg': newpassword})
    else:
        return JsonResponse({'status': 1})


def page_wait(request, content):
    return render(request, 'ldap/page_wait.html', locals())


def send_forget_password_email(request, pk):
    """
    普通LDAP用户重置密码
    :param request:
    :return:
    """
    error = ''
    template = 'ldap/send_forget_password_email.html'

    email_content_template = '<html><body>We heard that you lost your ops password. Sorry about that!' \
                             '<br><br>But don’t worry! You can use the following link to reset your password:' \
                             '<br><br>{domain}/accounts/ldap/email_reset_password/{token}' \
                             '<br><br>If you don’t use this link within 1 hours, it will expire. To get a new password reset link' \
                             '<br><br>Thanks,<br>The Ops Team<body></html>'

    if request.method == 'POST':
        email_prefix = request.POST['email_prefix']
        email_suffix = request.POST['email_suffix']
        print(email_prefix)
        print(email_suffix)
        # 校验邮箱是否存在于当前ldap账号中，不存在返回无效
        try:
            ad, ldap_group_dn, ldap_user_dn = ad_instance(pk)
            all_user = ad.get_user_list()
        except Exception as e:
            logger.error(e)
            return render(request, template, {"error": {"message": '内部错误,连接失败'}})
        this_dn = ''
        email = '{email_prefix}@{email_suffix}'.format(email_suffix=email_suffix, email_prefix=email_prefix)
        print(email)
        for i in all_user:
            if 'mail' in i['attributes']:
                if email in i['attributes']['mail']:
                    this_dn = i['dn']
                    break
        if this_dn == '':
            return render(request, template, {"error": {"message": '输入邮箱有误'}})
        # 生成随机验证串，邮箱，当前时间，dn ，一并存入数据库中
        token = random_str()
        LdapUserEmailVerifyRecord.objects.create(ldap_server_id=pk,
                                                 dn=this_dn,
                                                 token=token,
                                                 email=email)
        # 发邮件，包含验证串
        # 发送邮件功能-------------
        subject = '[{}] Please reset your password'.format(settings.SITE_NAME)  # 主题
        sender = settings.EMAIL_FROM  # 发送邮箱，已经在settings.py设置，直接导入
        receiver = [email]  # 目标邮箱
        html_message = email_content_template.format(token=token, domain=settings.DOMAIN_NAME)  # 发送html格式
        print(html_message)
        try:
            print(subject)
            print(sender,receiver)
            send_result = send_mail(subject=subject, from_email=sender, html_message=html_message, recipient_list=receiver,
                                    message='')
            print(send_result)
            if send_result == 1:
                # 提示邮件已发送，并跳转到登录页面
                return redirect("page_wait", content='密码重置邮件已经发送')
            else:
                return render(request, template, {"error": {"message": '内部错误'}})
        except Exception as e:
            logger.error(e)
            return render(request, template, {"error": {"message": '邮件发送失败'}})
        # 发送邮件功能结束----------
    return render(request, template, locals())


def email_reset_password(request, token):
    template = "ldap/reset_password.html"
    # 获取token，进入数据库查询，并比对时间，1小时以内的邮箱，有则返回
    error = ''
    try:
        find_result = LdapUserEmailVerifyRecord.objects.get(token=token)
    except Exception as e:
        logger.error(e)
        return redirect("page_wait", content='当前链接无效')
    now_time = timezone.now()
    if (now_time - find_result.create_at).seconds > 3600:
        return redirect("page_wait", content='当前链接已经过期')
    # 二次验证当前ldap账户，是否有这个邮箱，如果存在则返回重置密码窗口
    ad, group, people = ad_instance(find_result.ldap_server_id)
    all_user = ad.get_user_list()
    this_dn = ''
    for i in all_user:
        if 'mail' in i['attributes']:
            if find_result.email in i['attributes']['mail']:
                this_dn = i['dn']
                break
    if this_dn != find_result.dn or this_dn == '':
        return redirect("page_wait", content='重置密码链接验证失败')
    # 二次验证完成
    if request.method == 'POST':
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        # 校验密码复杂度
        pattern = re.compile("^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])[\s\S]{8,32}$")
        if pattern.match(password1) is None:
            return render(request, template, {"error": {"message": '须8-32个字符，至少包含1个大写字母，1个小写字母和1个数字'}})
        # 校验是否一致
        if password1 != password2:
            return render(request, template, {"error": {"message": '两次输入密码必须一致'}})
        # 保存并返回是否成功
        status, msg = ad.modify_password(this_dn, password1)
        if status:
            # 成功了要不要发个邮件呢，后面处理
            return redirect("page_wait", content='重置密码成功')
        else:
            return redirect("page_wait", content='重置密码失败')
    return render(request, template, locals())
