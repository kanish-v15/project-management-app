"""models.py"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    """Custom user model with role attribute."""
    ROLE_CHOICES = (
        ('Manager', 'Manager'),
        ('Team Lead', 'Team Lead'),
        ('Employee', 'Employee'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

class Project(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class ProjectBudget(models.Model):
    project = models.ForeignKey(Project, related_name='budgets', on_delete=models.CASCADE)
    month = models.CharField(max_length=50, null=True, blank=True)
    year = models.CharField(max_length=50, null=True, blank=True)
    budgeted_resources = models.DecimalField(max_digits=5, decimal_places=2)
    actual_resources = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    resource_details = models.TextField(null=True, blank=True)
    comments = models.ManyToManyField(settings.AUTH_USER_MODEL, through='ProjectComment', related_name='commented_projects', blank=True)

    def __str__(self):
        return f"{self.project.name} - {self.month} {self.year}"

class ProjectComment(models.Model):
    project_budget = models.ForeignKey(ProjectBudget, on_delete=models.CASCADE, null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.project_budget}"

class EmployeeResource(models.Model):
    project_budget = models.ForeignKey(ProjectBudget, related_name='employee_resources', on_delete=models.CASCADE)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    allocation_ratio = models.CharField(max_length=10)

    class Meta:
        unique_together = ('project_budget', 'employee')

    def __str__(self):
        return f"{self.employee.username} - {self.project_budget} ({self.allocation_ratio})"
