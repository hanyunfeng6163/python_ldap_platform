# Generated by Django 3.1 on 2020-11-09 11:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0022_auto_20201027_1145'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ldapserver',
            name='ldap_group_object_class',
            field=models.CharField(blank=True, choices=[('groupOfUniqueNames', 'groupOfUniqueNames')], default='groupOfUniqueNames', max_length=50, null=True, verbose_name='组对象类'),
        ),
        migrations.AlterField(
            model_name='ldapserver',
            name='ldap_user_object_class',
            field=models.CharField(blank=True, choices=[('inetOrgPerson', 'inetOrgPerson')], default='inetOrgPerson', max_length=50, null=True, verbose_name='用户对象类'),
        ),
        migrations.AlterField(
            model_name='userlogininfo',
            name='user',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.PROTECT, related_name='login_info', to=settings.AUTH_USER_MODEL),
        ),
    ]
