# Generated by Django 3.2.5 on 2021-10-03 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0010_auto_20210916_0934'),
    ]

    operations = [
        migrations.AlterField(
            model_name='like',
            name='value',
            field=models.IntegerField(blank=True, choices=[(1, 'VERY_BAD'), (2, 'BAD'), (3, 'OK'), (4, 'GOOD'), (5, 'PERFECT')], null=True, verbose_name='star'),
        ),
    ]