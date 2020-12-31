# Generated by Django 3.1 on 2020-10-25 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0015_auto_20201025_2315'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ldapserver',
            name='_password',
        ),
        migrations.AddField(
            model_name='ldapserver',
            name='password',
            field=models.CharField(default=1, max_length=100, verbose_name='管理密码'),
            preserve_default=False,
        ),
    ]
