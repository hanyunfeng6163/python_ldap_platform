import logging

import markdown
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render
from django.template.loader import get_template

# Create your views here.
from importlib import import_module
from django.conf import settings

logger = logging.getLogger('sso')


@login_required
def index(request):
    return render(request, 'index.html')


@login_required
def test(request):
    return render(request, 'ldap/test.html')


@login_required
def doc(request, name):
    template = get_template('doc.html')
    docfile = get_template('doc/{}.md'.format(name))

    md = markdown.Markdown(
        extensions=[
            # 包含 缩写、表格等常用扩展
            'markdown.extensions.extra',
            # 语法高亮扩展
            'markdown.extensions.codehilite',
            # 目录扩展
            'markdown.extensions.toc',
        ]
    )
    content = md.convert(docfile.render())
    return render(request, 'doc.html', locals())
