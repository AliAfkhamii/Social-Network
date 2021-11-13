# Generated by Django 3.2.5 on 2021-11-13 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_auto_20211030_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='pinned',
            field=models.BooleanField(default=False, verbose_name='pinned'),
        ),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(allow_unicode=True, blank=True, max_length=100, null=True, verbose_name='slug'),
        ),
    ]