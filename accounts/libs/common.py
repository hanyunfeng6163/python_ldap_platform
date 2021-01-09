# -*- coding: utf-8 -*
# @author: 韩云峰
# @time: 2019/3/20 17:51
import logging
from time import time
from random import random, Random
from urllib.parse import parse_qsl, urlunsplit, urlsplit
from uuid import uuid3, NAMESPACE_URL

import pypinyin
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

from accounts.libs.con_ldap import AD
from accounts.models import User, LdapServer
from django.core.mail import send_mail
from django.http import HttpResponseRedirect

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from accounts.libs import con_redis
from accounts.models import UserLoginInfo
from common.lib import rsa_decrypt

logger = logging.getLogger('sso')

redis_conn = con_redis.cacheRedis()


def auth_interceptor(user):
    """
    帐号锁待处理
    :param user:
    :return:
    """
    if user.is_lock:
        return False, '当前用户已经锁定，请联系管理员'
    else:
        return True, '验证成功'


def login_info(request, user, source, ldap_server=None):
    """
    记录用户登录的ip地址、时间、登录方式
    :param request:
    :param user:
    :param source:
    :return:
    """
    try:
        if 'HTTP_X_FORWARDED_FOR' in request.META:
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        obj, created = UserLoginInfo.objects.get_or_create(user=user)
        obj.source = source
        obj.login_ip = ip
        if ldap_server is not None:
            obj.ldap_server = ldap_server
        obj.save()
        return True, '记录成功!'
    except Exception as e:
        logger.error(e)
        return False, '登陆失败!'


def auth(request, username, password):
    """
    本地登录验证
    :param request:
    :param username:
    :param password:
    :return:
    """
    user = authenticate(username=username, password=password)
    if user is not None:

        # 验证用户是否锁定
        interceptor_user = auth_interceptor(user)
        if not interceptor_user[0]:
            return False, interceptor_user[1]

        # 登录用户
        login(request, user)

        # 记录登录信息
        info_user = login_info(request, user, 'local')
        if not info_user[0]:
            logout(request)
            return False, info_user[1]

        return True, '登陆成功!'
    else:
        return False, '用户名或密码错误'


def ldap_auth(request, ldapserver_id, username, password):
    """
    ldap登录验证
    :param request:
    :param username:
    :param password:
    :return:
    """
    l_s = LdapServer.objects.get(id=ldapserver_id)
    try:
        ad = AD(host=l_s.host, port=l_s.port, user=l_s.user, password=rsa_decrypt(l_s.password),
                base_dn=l_s.ldap_base_dn)
    except Exception as e:
        logger.error(e)
        return False, '认证服务器连接失败'
    check_status, user_info = ad.check_password(username=username, password=password)
    print(user_info)
    if check_status:
        # ldap认证成功
        # 判断本地是否存在
        _user = get_or_none(User, username=username)
        if _user is None:
            _user = User.objects.create(username=username, nickname=user_info['nickname'], email=user_info['email'],
                                        phone=user_info['phone'], source='ldap')
        # 验证用户是否锁定
        interceptor_user = auth_interceptor(_user)
        if not interceptor_user[0]:
            return False, interceptor_user[1]
        login(request, _user)
        # 记录登录信息
        info_user = login_info(request=request, user=_user, source='ldap', ldap_server=l_s.id)
        if not info_user[0]:
            logout(request)
            return False, info_user[1]
        return True, '登陆成功!'
    else:
        return False, '用户名或者密码错误'


def get_service(request, refererForward=None):
    if refererForward is None:
        refererForward = settings._DEFAULT_FORWARD

    next = request.GET.get("next", refererForward)
    service = request.GET.get("service", next)
    serviceObj = urlsplit(service)
    if not serviceObj.netloc:
        return service, None

    query = ''
    url = urlunsplit((serviceObj.scheme, serviceObj.netloc, serviceObj.path, query, serviceObj.fragment))
    modifyUrl = '%s?' % url
    return modifyUrl, serviceObj.netloc


def make_ticket(username, remote_addr):
    ticket = "%s%d%s%f" % (username, time(), remote_addr, random())
    return str(uuid3(NAMESPACE_URL, ticket))


def cache_user(username, ticket, domain, nickname=None, email=None, phone=None, role=None):
    """
    无论使用钉钉、ldap或者本地登录，当获取角色、email、phone等信息的时候，都是从本地的数据库取获取。
    如果本地没有，则使用登录源去同步
    这个通过用户名来获取其他用户信息
    :param username:
    :param ticket:
    :param domain:
    :param nickname:
    :param email:
    :param phone:
    :param role:
    :return:
    """
    t_data = {
        "username": username,
        "ticket": ticket,
        "domain": domain,
    }
    try:
        _user = User.objects.get(username=username)

        role_list = []
        for i in _user.roles.all():
            role_list.append(i.mark)
        t_data['roles'] = str(role_list)

        if _user.nickname is None:
            t_data['nickname'] = ''
        else:
            t_data['nickname'] = _user.nickname

        t_data['email'] = _user.email

        if _user.phone is None:
            t_data['phone'] = ''
        else:
            t_data['phone'] = _user.phone
    except Exception as e:
        logger.error(e)

    return redis_conn.setTicket(settings._TIME_OUT, **t_data)


def combine_ticket(service, ticket):
    finall = service + '%s=%s' % (settings._TICKET_NAME, ticket)
    return finall


def cache_logout_user(ticket):
    if ticket:
        return redis_conn.delTicket(ticket)
    return True


def get_user_by_ticket(ticket):
    data = redis_conn.findTicket(ticket)
    if data:
        return data
    else:
        return None


def login_redirect(request, service, domain, username):
    remote_addr = request.META.get("REMOTE_ADDR")
    t = request.session.get(settings._TICKET_NAME)
    if t:
        cache_logout_user(t)
    if domain:
        ticket = make_ticket(username, remote_addr)
        request.session[settings._TICKET_NAME] = ticket
        cache_user(username, ticket, domain)
        return HttpResponseRedirect(combine_ticket(service, ticket))
    return HttpResponseRedirect(service)


def get_referer_service(request):
    referer = request.META.get("HTTP_REFERER")
    if not referer:
        return False
    res = urlsplit(referer).netloc
    if res:
        return res
    else:
        return False


def pagination(request, queryset, display_amount=10, after_range_num=8, before_range_num=7):
    try:
        page = int(request.GET.get("page", 1))
        if page < 1:
            page = 1
    except ValueError:
        page = 1

    paginator = Paginator(queryset, display_amount)
    count = paginator.count
    num_pages = paginator.num_pages
    try:
        objects = paginator.page(page)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        objects = paginator.page(1)
    temp_range = paginator.page_range
    if (page - before_range_num) <= 0:
        if temp_range[-1] > after_range_num:
            page_range = range(1, after_range_num + 1)
        else:
            page_range = range(1, temp_range[-1] + 1)
    elif (page + after_range_num) > temp_range[-1]:
        page_range = range(page - before_range_num, temp_range[-1] + 1)
    else:
        page_range = range(page - before_range_num +
                           1, page + after_range_num)
    return objects, page_range, count, num_pages


def pinyin(word):
    s = ''
    for i in pypinyin.pinyin(word, style=pypinyin.NORMAL):
        s += ''.join(i)
    return s


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None


class IsAdminMixin(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect("page_wait", content='您没有此页面权限')
        else:
            return super().dispatch(request, *args, **kwargs)


def send_ali_password(username, nickname, email, password):
    email_content_template = '<html><body>{nickname}, 您好：' \
                             '<br>我们为您开通了阿里云子账号!' \
                             '<br><br>用户名: {username}{account_mail}' \
                             '<br>密码: {password}' \
                             '<br><br>当您第一次登陆的时候，我们会要求您重置密码' \
                             '<br><br>Thanks,<br>The Ops Team<body></html>'
    subject = '[运维通知] 阿里云子账号开通提醒'
    sender = settings.EMAIL_FROM  # 发送邮箱，已经在settings.py设置，直接导入
    receiver = [email]  # 目标邮箱
    html_message = email_content_template.format(username=username, nickname=nickname, password=password,
                                                 account_mail=settings.ACCOUNT_MAIL)  # 发送html格式

    try:
        print(subject)
        print(sender, receiver)
        send_result = send_mail(subject=subject, from_email=sender, html_message=html_message, recipient_list=receiver,
                                message='')
        print(send_result)
        if send_result == 1:
            # 提示邮件已发送，并跳转到登录页面
            return True
        else:
            return False
    except Exception as e:
        logger.error(e)
        return False


def send_ldap_password(username, nickname, email, password):
    email_content_template = '<html><body>{nickname}, 您好：' \
                             '<br>我们为您开通了统一账号' \
                             '<br><br>用户名: {username}' \
                             '<br>密码: {password}' \
                             '<br><br>重置或修改密码可以访问 {sso_address}' \
                             '<br>您可以使用此账号登录内部系统,详情参见内部wiki' \
                             '<br><br>Thanks,<br>The Ops Team<body></html>'
    subject = '[运维通知] 统一账号开通提醒'
    sender = settings.EMAIL_FROM  # 发送邮箱，已经在settings.py设置，直接导入
    receiver = [email]  # 目标邮箱
    html_message = email_content_template.format(username=username, nickname=nickname, password=password,
                                                 sso_address=settings.DOMAIN_NAME)  # 发送html格式

    try:
        print(subject)
        print(sender, receiver)
        send_result = send_mail(subject=subject, from_email=sender, html_message=html_message, recipient_list=receiver,
                                message='')
        print(send_result)
        if send_result == 1:
            # 提示邮件已发送，并跳转到登录页面
            return True
        else:
            return False
    except Exception as e:
        logger.error(e)
        return False
