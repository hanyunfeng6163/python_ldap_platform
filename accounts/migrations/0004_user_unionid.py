# Generated by Django 3.1 on 2020-09-21 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_auto_20200914_2351'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='unionid',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
