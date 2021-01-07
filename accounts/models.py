from django.db import models

# Create your models here.

from django.contrib.auth.models import UserManager, AbstractBaseUser
from django.utils import timezone

from common.lib import rsa_encrypt


class User(AbstractBaseUser):
    username = models.CharField(max_length=40, unique=True, db_index=True)
    nickname = models.CharField(max_length=64, null=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    source = models.CharField(max_length=10, blank=True, null=True, default='local')  # 账户来源
    is_lock = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    roles = models.ManyToManyField(verbose_name='拥有的所有角色', to='Role', blank=True)
    unionid = models.CharField(max_length=64, blank=True, null=True)
    objects = UserManager()
    USERNAME_FIELD = 'username'

    def has_module_perms(self, app_label):
        return self.is_superuser

    def has_perm(self, perm, obj=None):
        if self.is_active and self.is_superuser:
            return True


class Role(models.Model):
    """
    角色表
    """
    title = models.CharField(verbose_name='角色名称', max_length=32, unique=True)
    mark = models.CharField(verbose_name='角色代号', max_length=20, unique=True)
    external_permission = models.ManyToManyField(verbose_name='拥有的权限', to='ExternalPermission', blank=True)

    def __str__(self):
        return self.title


class ExternalPermission(models.Model):
    """
    外置权限表
    """
    title = models.CharField(verbose_name='权限名称名称', max_length=32, unique=True)
    mark = models.CharField(verbose_name='权限简称', max_length=20, unique=True)

    class Meta:
        verbose_name = u'外部权限表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class UserLoginInfo(models.Model):
    SOURCE_CHOICES = (
        ('local', u"本地登录"),
        ('ldap', u"LDAP登录"),
        ('ding', u"钉钉登录"),
    )
    user = models.OneToOneField(User, on_delete=models.PROTECT, default=None, related_name='login_info')
    login_time = models.DateTimeField('最后登录时间', auto_now=True)
    login_ip = models.CharField(u"最后登录ip", max_length=40, default='')
    source = models.CharField(u"最后登录方式", max_length=30, default='local', choices=SOURCE_CHOICES)
    ldap_server = models.CharField(max_length=128, blank=True, null=True)

    def __unicode__(self):
        return '%s,%s,%s' % (self.user.username, self.login_time, self.login_ip)

    class Meta:
        verbose_name = u'用户登录信息'
        verbose_name_plural = verbose_name


class DomainuthorizedList(models.Model):
    name = models.CharField(u"简介", max_length=100)
    mark = models.CharField(u"英文标记", max_length=100, unique=True)
    domain_name = models.CharField(u"域名", max_length=100)
    logout_api_url = models.CharField(u"登出接口地址", max_length=100)


class WebAuthorizationRecord(models.Model):
    STATUS = (
        (0, u"已经登出"),
        (1, u"登录中"),
    )
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True)
    status = models.IntegerField(u"应用状态", choices=STATUS, null=True, blank=True, default=1)
    tag = models.CharField(u"标志", max_length=100, null=True, blank=True)
    domain = models.ForeignKey(DomainuthorizedList, on_delete=models.PROTECT, null=True, blank=True)
    create_at = models.DateTimeField(u'创建时间', auto_now_add=True)


class LdapServer(models.Model):
    LDAP_TYPE = (
        ('openladp', 'openladp'),
        ('windows_ad', 'windows_ad'),
    )
    USER_OBJ = (
        ('inetOrgPerson', 'inetOrgPerson'),
    )
    GROUP_OBJ = (
        ('groupOfUniqueNames', 'groupOfUniqueNames'),
    )
    host = models.CharField(u"地址", max_length=40, unique=True, db_index=True)
    port = models.IntegerField(u"端口", default=389)
    user = models.CharField(u"管理用户", max_length=100)
    password = models.CharField(u"管理密码", max_length=100)
    use_ssl = models.BooleanField(default=False)
    ldap_server = models.CharField(choices=LDAP_TYPE, verbose_name='ldap类型', max_length=30, default='openldap')
    desc = models.CharField(u"描述", max_length=64, blank=True, null=True)
    ldap_base_dn = models.CharField(u"基本DN", max_length=100, null=True, blank=True)
    ldap_user_dn = models.CharField(u"附加用户DN", max_length=50, null=True, blank=True)
    ldap_group_dn = models.CharField(u"附加组DN", max_length=50, null=True, blank=True)
    ldap_user_object_class = models.CharField(u"用户对象类", choices=USER_OBJ, max_length=50, null=True, blank=True,
                                              default='inetOrgPerson')
    ldap_group_object_class = models.CharField(u"组对象类", choices=GROUP_OBJ, max_length=50, null=True, blank=True,
                                               default='groupOfUniqueNames')

    def save(self, *args, **kwargs):
        self.password = rsa_encrypt(self.password)
        super(LdapServer, self).save(*args, **kwargs)


# 组织架构，用户和组织的关系呢


class LdapUserEmailVerifyRecord(models.Model):
    """
    ldap 普通用户重置密码token验证表
    """
    dn = models.EmailField(max_length=100, null=True, blank=True)
    email = models.EmailField(max_length=255, null=True, blank=True)
    token = models.CharField(u"token", max_length=300, null=True, blank=True)
    ldap_server_id = models.IntegerField(u"ldap服务id", null=True, blank=True)
    create_at = models.DateTimeField(u'创建时间', auto_now_add=True)
