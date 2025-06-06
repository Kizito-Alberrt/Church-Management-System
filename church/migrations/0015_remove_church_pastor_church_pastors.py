# Generated by Django 5.2.1 on 2025-05-23 21:31

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('church', '0014_user_pastor_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='church',
            name='pastor',
        ),
        migrations.AddField(
            model_name='church',
            name='pastors',
            field=models.ManyToManyField(blank=True, limit_choices_to={'role': 'Pastor'}, related_name='churches', to=settings.AUTH_USER_MODEL),
        ),
    ]
