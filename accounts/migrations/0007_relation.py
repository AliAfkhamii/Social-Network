# Generated by Django 3.2.6 on 2021-09-15 16:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_remove_profile_posts_liked'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followers', to='accounts.profile', verbose_name='following')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='followings', to='accounts.profile', verbose_name='follower')),
            ],
            options={
                'verbose_name': 'relation',
                'verbose_name_plural': 'relations',
                'unique_together': {('follower', 'account')},
            },
        ),
    ]