import logging

from django.contrib.auth import login, logout
from django.shortcuts import render

from accounts.models import User, DomainuthorizedList
from accounts.libs.common import pinyin, get_service, login_redirect, login_info
import requests

logger = logging.getLogger('sso')


def ding_callback(request):
   pass

