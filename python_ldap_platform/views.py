from django.conf import settings


def global_setting(request):
    """
    全局返回变量给模板
    :param request:
    :return:
    """
    return {
        'SITE_NAME': settings.SITE_NAME,  # 网站名称
        'DOMAIN_NAME': settings.DOMAIN_NAME,  # 网站地址
        'DOMAIN_SUFFIX': settings.DOMAIN_SUFFIX, # 域名后缀
    }

