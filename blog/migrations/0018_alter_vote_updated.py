# Generated by Django 3.2.5 on 2021-11-24 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0017_auto_20211124_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='updated',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date updated'),
        ),
    ]