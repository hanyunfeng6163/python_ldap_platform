import json
import logging
import os

import requests

from django.conf import settings
from django.contrib.auth import logout, get_user_model
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from accounts.libs.common import get_service, login_redirect, auth, get_user_by_ticket, get_referer_service, \
    cache_logout_user, ldap_auth
from accounts.models import WebAuthorizationRecord, DomainuthorizedList, LdapServer

logger = logging.getLogger('sso')


def web_login(request):
    try:
        l_s = LdapServer.objects.all()
    except Exception as e:
        logger.error(e)
        pass
    template = 'accounts/login.html'
    error = ''
    service, domain = get_service(request)
    # 增加针对域名进行授权的功能
    # 如果为None 表示当前登录为本地登录
    if domain is not None:
        try:
            domain_count = DomainuthorizedList.objects.filter(domain_name=domain).count()
        except Exception as e:
            domain_count = 0
        if domain_count == 0:
            error = "当前网站不在授权列表内，请联系管理员"
            return render(request, template, locals())
    # 增加针对域名进行授权的功能 结束
    if request.user.is_authenticated:
        return login_redirect(request, service, domain, request.user.username)
    if request.method == 'POST':
        # 认证方式区分
        if 'username' in request.POST:
            username = request.POST.get("username")
            password = request.POST.get("password")
            auth_reault = auth(request, username, password)
        elif 'ldap_username' in request.POST:
            ldapserver_id = request.POST.get("ldapserver_id")
            username = request.POST.get("ldap_username")
            password = request.POST.get("ldap_password")
            auth_reault = ldap_auth(request, ldapserver_id, username, password)
        else:
            error = "认证方式获取失败"
            return render(request, template, locals())
        # 返回
        if auth_reault[0]:
            return login_redirect(request, service, domain, username)
        else:
            error = auth_reault[1]
            return render(request, template, locals())
    else:
        return render(request, template, locals())


def ticket_check(request):
    ticket = str(request.GET.get(settings._TICKET_NAME, None))
    status = {"result": False, "user": False, settings._TICKET_NAME: ticket, 'message': None, 'nickname': None,
              'email': None}

    if ticket is None:
        status['message'] = 'No ticket'
        return HttpResponse(json.dumps(status), content_type="application/json")

    loginCacheData = get_user_by_ticket(ticket)

    if loginCacheData is None:
        status['message'] = 'Bad ticket'
        return HttpResponse(json.dumps(status), content_type="application/json")

    domain = get_referer_service(request)
    if not domain:
        status['message'] = "No domain"
        return HttpResponse(json.dumps(status), content_type="application/json")

    if domain != loginCacheData['domain']:
        status['message'] = 'Domain not compaire'
        return HttpResponse(json.dumps(status), content_type="application/json")

    status['user'] = loginCacheData['username']
    status['result'] = True
    status['message'] = 'Success'
    # 暂时只返回user
    return HttpResponse(status['user'])


def login_status(request, web_tag, username, session_tag):
    """
    负责接收客户端的登录session登信息，用来记录和统一退出操作
    :param request:
    :param web_tag:
    :param username:
    :param session_tag:
    :return:
    """
    try:
        user = get_user_model().objects.get(username=username)
        domain = DomainuthorizedList.objects.get(mark=web_tag)
        WebAuthorizationRecord.objects.create(user=user, tag=session_tag, domain=domain)
        status = 0
    except Exception as e:
        logger.error(e)
        status = 1
    return HttpResponse(status)


def logout_user(request):
    t = request.session.get(settings._TICKET_NAME)
    if t:
        cache_logout_user(t)
    request.session.clear()
    logout(request)


def web_logout(request):
    service, domain = get_service(request, settings._LOGIN_URL)
    if request.user.is_authenticated:
        user = request.user
        logout_user(request)
        # 统一退出客户机
        for i in WebAuthorizationRecord.objects.filter(user=user, status=1):
            try:
                requests.get(os.path.join(i.domain.logout_api_url, i.tag), timeout=5)
                i.status = 0
                i.save()
            except Exception as e:
                logger.error(e)
    return HttpResponseRedirect(service)
