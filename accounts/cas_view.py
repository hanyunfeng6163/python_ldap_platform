# -*- coding: utf-8 -*
# @author: 韩云峰
# @time: 2019/3/20 17:51
# @describe: 为了适配cas v3协议，增加了一个ticket校验类，后面有需求再进行补充

from django.utils.encoding import force_text
from accounts.libs.common import get_user_by_ticket

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import xml.etree.ElementTree as etree

from django.http import HttpResponse
from django.views.generic.base import View


class ValidationResponse(HttpResponse):
    pass

class ServiceValidateView(View):
    pass
