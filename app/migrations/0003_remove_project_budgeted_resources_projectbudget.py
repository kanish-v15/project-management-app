# Generated by Django 5.1 on 2024-10-14 08:45

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_remove_project_employees_remove_project_lead_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='budgeted_resources',
        ),
        migrations.CreateModel(
            name='ProjectBudget',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('period', models.CharField(max_length=50)),
                ('budgeted_resources', models.DecimalField(decimal_places=2, max_digits=5)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='budgets', to='app.project')),
            ],
        ),
    ]