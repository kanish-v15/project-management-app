"""admin.py"""

from django.contrib import admin
from .models import Project, User, EmployeeResource

admin.site.register(Project)
admin.site.register(User)
admin.site.register(EmployeeResource)
