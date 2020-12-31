# Generated by Django 3.1 on 2020-09-10 23:40

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(db_index=True, max_length=40, unique=True)),
                ('nickname', models.CharField(max_length=64, null=True)),
                ('email', models.EmailField(max_length=255, null=True, unique=True)),
                ('phone', models.CharField(blank=True, max_length=64, null=True)),
                ('is_lock', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='DomainuthorizedList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='简介')),
                ('mark', models.CharField(max_length=100, unique=True, verbose_name='英文标记')),
                ('domain_name', models.CharField(max_length=100, verbose_name='域名')),
                ('logout_api_url', models.CharField(max_length=100, verbose_name='登出接口地址')),
            ],
        ),
        migrations.CreateModel(
            name='WebAuthorizationRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(blank=True, choices=[(0, '已经登出'), (1, '登录中')], default=1, null=True, verbose_name='应用状态')),
                ('tag', models.CharField(blank=True, max_length=100, null=True, verbose_name='标志')),
                ('domain', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.domainuthorizedlist')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserLoginInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_time', models.DateTimeField(auto_now=True, verbose_name='登录时间')),
                ('login_ip', models.CharField(default='', max_length=40, verbose_name='登录ip')),
                ('source', models.CharField(choices=[('local', '本地登录'), ('ldap', 'LDAP登录'), ('ding', '钉钉登录')], default='local', max_length=30, verbose_name='登录方式')),
                ('user', models.OneToOneField(default=None, on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': '用户登录信息',
                'verbose_name_plural': '用户登录信息',
            },
        ),
    ]