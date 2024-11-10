# Generated by Django 5.1 on 2024-10-16 14:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_remove_project_comments_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='actual_resources',
        ),
        migrations.RemoveField(
            model_name='project',
            name='resource_details',
        ),
        migrations.RemoveField(
            model_name='project',
            name='start_month',
        ),
        migrations.RemoveField(
            model_name='projectbudget',
            name='period',
        ),
        migrations.RemoveField(
            model_name='projectcomment',
            name='project',
        ),
        migrations.AddField(
            model_name='projectbudget',
            name='actual_resources',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=4, null=True),
        ),
        migrations.AddField(
            model_name='projectbudget',
            name='comments',
            field=models.ManyToManyField(blank=True, related_name='commented_projects', through='app.ProjectComment', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='projectbudget',
            name='month',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='projectbudget',
            name='resource_details',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='projectbudget',
            name='year',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='projectcomment',
            name='project_budget',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='app.projectbudget'),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='projectcomment',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
