"""views.py"""

from datetime import datetime
import calendar
from decimal import Decimal, InvalidOperation
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.http import urlencode
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.db import IntegrityError
from django.db.models import Sum
from .forms import CustomUserCreationForm, EmployeeForm, ProjectForm, ProjectBudgetForm  
from .models import Project, ProjectBudget, ProjectComment, EmployeeResource

User = get_user_model()

def register(request):
    """Registers new user"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    """Logins user"""
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    """Logout user"""
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    """Render the dashboard based on the user's role."""
    projects = Project.objects.all()
    
    if request.user.role == 'Manager':
        return render(request, 'manager_dashboard.html', {'projects': projects})
    elif request.user.role == 'Team Lead':
        return render(request, 'team_lead_dashboard.html', {'projects': projects})
    elif request.user.role == 'Employee':
        return render(request, 'employee_dashboard.html', {'projects': projects})
    else:
        return redirect('login')

@login_required
def create_project(request):
    """View to create a new project with a specified budgeted resources and month-year."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        budget_form = ProjectBudgetForm(request.POST)
        if form.is_valid() and budget_form.is_valid():
            project = form.save()  

            budget = budget_form.save(commit=False)
            budget.project = project
            budget.save()

            messages.success(request, "Project created successfully.")
            return redirect('manager_dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProjectForm()
        budget_form = ProjectBudgetForm()

    return render(request, 'create_project.html', {'form': form, 'budget_form': budget_form})

@login_required
def project_details(request, project_id):
    """View to display the details of a specific project and allow filtering by period."""
    project = get_object_or_404(Project, pk=project_id)
    start_month = project.budgets.first().month
    start_year = project.budgets.first().year

    start_month_idx = list(calendar.month_abbr).index(start_month)
    start_year = int(start_year)

    available_periods = []
    for i in range(6):
        next_month = (start_month_idx + i - 1) % 12 + 1
        next_year = start_year + ((start_month_idx + i - 1) // 12)
        available_periods.append(f"{calendar.month_abbr[next_month]} {next_year}")

    selected_period = request.GET.get('period', available_periods[0])  # Default to the first period if none is selected

    try:
        month, year = selected_period.split()
    except ValueError:
        month, year = None, None

    budget = ProjectBudget.objects.filter(project=project, month=month, year=year).first()

    recent_comments = ProjectComment.objects.filter(project_budget=budget).order_by('-created_at') if budget else None

    employee_resources = EmployeeResource.objects.filter(project_budget=budget) if budget else []

    actual_resources = Decimal(
        sum(
            float(resource.allocation_ratio) 
            for resource in employee_resources 
            if isinstance(resource.allocation_ratio, (int, float)) or 
            resource.allocation_ratio.lower() not in ['intern', 'interns']
        )
    )

    profit_rating = Decimal(budget.budgeted_resources) - actual_resources if budget else None
    profit_loss_percentage = (
        (profit_rating / Decimal(budget.budgeted_resources)) * 100 if budget and budget.budgeted_resources != 0 else None
    )

    if request.method == 'POST' and 'comment_text' in request.POST:
        comment_text = request.POST['comment_text']
        if comment_text and budget:
            ProjectComment.objects.create(
                project_budget=budget,
                user=request.user,
                text=comment_text
            )
            return redirect('project_details', project_id=project.id)

    return render(request, 'project_details.html', {
        'project': project,
        'budget': budget,
        'available_periods': available_periods,
        'selected_period': selected_period,
        'recent_comments': recent_comments,
        'employee_resources': employee_resources,
        'actual_resources': actual_resources,
        'profit_rating': profit_rating,
        'profit_loss_percentage': profit_loss_percentage,
    })

@login_required
def edit_project(request, project_id):
    """Handle project editing by the manager.

    Args:
        request: The HTTP request object.
        project_id: The ID of the project.

    Returns:
        HTTP response with the project edit form or redirects to the manager dashboard on successful edit.
    """
    project = get_object_or_404(Project, pk=project_id)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('manager_dashboard')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'edit_project.html', {'form': form, 'project': project})

@login_required
def delete_project(request, project_id):
    """View to delete a specific project."""
    project = get_object_or_404(Project, pk=project_id)

    if request.user.role == 'Manager':
        project.delete()
        return redirect('manager_dashboard')

    return redirect('project_details', project_id=project.id)

@login_required
def add_comment(request, project_id):
    """Handle adding a comment to a specific period of a project."""
    project = get_object_or_404(Project, pk=project_id)
    period = request.GET.get('period')

    if request.method == 'POST' and 'comment_text' in request.POST:
        comment_text = request.POST.get('comment_text')
        if comment_text and period:
            try:
                month, year = period.split()
            except ValueError:
                messages.error(request, "Invalid period format.")
                return redirect('project_details', project_id=project.id)

            budget = ProjectBudget.objects.filter(project=project, month=month, year=year).first()
            if budget:
                ProjectComment.objects.create(
                    project_budget=budget,
                    user=request.user,
                    text=comment_text
                )
                messages.success(request, "Comment added successfully.")
                return redirect(f"{reverse('project_details', args=[project.id])}?period={period}")

    messages.error(request, "Failed to add comment. Please try again.")
    return redirect('project_details', project_id=project.id)

@login_required
def edit_comment(request, comment_id):
    """Handle editing a comment on a specific project."""
    comment = get_object_or_404(ProjectComment, pk=comment_id)
    period = request.GET.get('period')
    if request.method == 'POST':
        comment_text = request.POST.get('comment_text')
        if comment_text:
            comment.text = comment_text
            comment.save()
            messages.success(request, "Comment edited successfully.")
            return redirect(f"{reverse('project_details', args=[comment.project_budget.project.id])}?period={period}")

    return render(request, 'edit_comment.html', {'comment': comment, 'period': period})

@login_required
def delete_comment(request, comment_id):
    """Handle deleting a comment from a project."""
    comment = get_object_or_404(ProjectComment, pk=comment_id)
    project_id = comment.project_budget.project.id
    period = request.GET.get('period')

    if request.method == 'POST':
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        return redirect(f"{reverse('project_details', args=[project_id])}?period={period}")

    return redirect('project_details', project_id=project_id)

@login_required
def edit_budgeted_resources(request, project_id):
    """Handle editing the budgeted resources for a specific month and year of a project."""
    project = get_object_or_404(Project, pk=project_id)
    period = request.GET.get('period')
    if request.user.role != 'Manager':
        return redirect('project_details', project_id=project.id)

    if not period:
        messages.error(request, "No period selected.")
        return redirect('project_details', project_id=project.id)

    try:
        month, year = period.split()
    except ValueError:
        messages.error(request, "Invalid period format. Please try again.")
        return redirect('project_details', project_id=project.id)

    budget = ProjectBudget.objects.filter(project=project, month=month, year=year).first()

    if request.method == 'POST':
        try:
            new_budgeted_resources = float(request.POST.get('budgeted_resources'))
            if 0 <= new_budgeted_resources <= 10 and round(new_budgeted_resources, 2) == new_budgeted_resources:
                if not budget:
                    budget = ProjectBudget(project=project, month=month, year=year)
                budget.budgeted_resources = new_budgeted_resources
                budget.save()
                messages.success(request, "Budgeted resources updated successfully.")
                return redirect(f"{reverse('project_details', kwargs={'project_id': project.id})}?period={period}")
            else:
                error_message = "Budgeted resources must be between 0 and 10, with up to two decimal places."
        except ValueError:
            error_message = "Please enter a valid number for budgeted resources."

    else:
        error_message = None

    return render(request, 'edit_budgeted_resources.html', {
        'project': project,
        'budget': budget,
        'period': period,
        'error_message': error_message,
    })

@login_required
def team_lead_dashboard(request):
    """View to render the dashboard for Team Leads."""
    if request.user.role != 'Team Lead':
        return redirect('dashboard')

    projects = Project.objects.all()
    return render(request, 'team_lead_dashboard.html', {'projects': projects})

@login_required
def employee_dashboard(request):
    """View to render the dashboard for Employees."""
    if request.user.role != 'Employee':
        return redirect('dashboard')

    projects = Project.objects.all()
    return render(request, 'employee_dashboard.html', {'projects': projects})

@login_required
def manage_resources(request, project_id):
    """View to manage resources for a specific project period."""
    project = get_object_or_404(Project, pk=project_id)
    selected_period = request.GET.get('period', None)

    if not selected_period:
        messages.error(request, "Period is required to manage resources.")
        return redirect('project_details', project_id=project.id)

    month, year = selected_period.split()
    project_budget = ProjectBudget.objects.filter(project=project, month=month, year=year).first()

    if not project_budget:
        messages.error(request, f"No budget allocated for {selected_period}. Please allocate budget first.")
        return redirect('project_details', project_id=project.id)

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        allocation_ratio = request.POST.get('allocation_ratio')

        if employee_id and allocation_ratio:
            try:
                employee = get_object_or_404(User, pk=employee_id)
                EmployeeResource.objects.create(
                    employee=employee,
                    project_budget=project_budget,
                    allocation_ratio=allocation_ratio
                )
                messages.success(request, "Resource added successfully.")
            except IntegrityError:
                messages.error(request, "This employee has already been assigned to this project budget.")
            except Exception as e:
                messages.error(request, f"An error occurred: {e}")

        base_url = reverse('manage_resources', kwargs={'project_id': project.id})
        query_string = urlencode({'period': selected_period})
        url = f"{base_url}?{query_string}"
        return HttpResponseRedirect(url)

    employee_resources = EmployeeResource.objects.filter(project_budget=project_budget)
    employees = User.objects.filter(is_active=True).exclude(employeeresource__project_budget=project_budget)

    return render(request, 'manage_resources.html', {
        'project': project,
        'project_budget': project_budget,
        'employee_resources': employee_resources,
        'employees': employees,
    })

@login_required
def edit_employee_resource(request, resource_id):
    """Edit an employee or team lead's resource allocation."""
    resource = get_object_or_404(EmployeeResource, pk=resource_id)
    project_id = resource.project_budget.project.id
    period = f"{resource.project_budget.month} {resource.project_budget.year}"

    if request.method == 'POST':
        allocation_ratio = request.POST.get('allocation_ratio')
        allowed_values = ["0.10", "0.20", "0.25", "0.30", "0.40", "0.50", "0.60", "0.70", "0.75", "0.80", "0.90", "1", "intern"]

        if allocation_ratio and allocation_ratio in allowed_values:
            try:
                if allocation_ratio != "intern":
                    allocation_ratio = Decimal(allocation_ratio)

                if allocation_ratio == "intern" or (Decimal('0') <= allocation_ratio <= Decimal('1')):
                    same_month_allocations = EmployeeResource.objects.filter(
                        employee=resource.employee,
                        project_budget__month=resource.project_budget.month,
                        project_budget__year=resource.project_budget.year
                    ).exclude(pk=resource_id)

                    total_allocation = same_month_allocations.aggregate(total=Sum('allocation_ratio'))['total'] or Decimal('0')

                    if allocation_ratio == "intern" or total_allocation + allocation_ratio <= Decimal('1'):
                        resource.allocation_ratio = allocation_ratio
                        resource.save()
                        messages.success(request, "Resource updated successfully.")
                        url = reverse('manage_resources', kwargs={'project_id': project_id})
                        return HttpResponseRedirect(f"{url}?period={period}")
                    else:
                        messages.error(request, f"Total allocation ratio cannot exceed 1 for {resource.employee.username} in {period}.")
                else:
                    messages.error(request, "Allocation ratio must be between 0 and 1.")
            except InvalidOperation:
                messages.error(request, "Invalid value for allocation ratio.")
        else:
            messages.error(request, "Invalid allocation ratio value.")

    return render(request, 'edit_employee_resource.html', {
        'resource': resource,
        'project_id': project_id,
        'period': period,
    })

@login_required
def delete_employee_resource(request, resource_id):
    """Delete an employee or team lead's resource from a project."""
    try:
        resource = EmployeeResource.objects.get(pk=resource_id)
        project_id = resource.project_budget.project.id
        period = f"{resource.project_budget.month} {resource.project_budget.year}"
    except EmployeeResource.DoesNotExist:
        messages.error(request, "The resource you are trying to delete does not exist.")
        return redirect('manager_dashboard')

    if request.method == 'POST':
        resource.delete()
        messages.success(request, "Resource deleted successfully.")
        url = reverse('manage_resources', kwargs={'project_id': project_id})
        return HttpResponseRedirect(f"{url}?period={period}")
    return render(request, 'delete_employee_resource.html', {
        'resource': resource,
    })

@login_required
def check_allocation_conflict(request, employee_id):
    """Check if adding the specified allocation ratio would exceed 1 for the given employee or team lead."""
    try:
        allocation_ratio = float(request.GET.get('allocation_ratio', 0))
        month = request.GET.get('month')
        year = request.GET.get('year')

        same_month_allocations = EmployeeResource.objects.filter(
            employee__id=employee_id,
            project_budget__month=month,
            project_budget__year=year
        )

        total_allocation = sum(resource.allocation_ratio for resource in same_month_allocations)
        
        if total_allocation + allocation_ratio > 1:
            return JsonResponse({'conflict': True})
        else:
            return JsonResponse({'conflict': False})

    except ValueError:
        return JsonResponse({'conflict': True, 'error': 'Invalid data provided.'})

@login_required
def resource_allocation_overview(request):
    """View to display an overview of resource allocations for team leads and employees."""
    year = request.GET.get('year', None)
    month = request.GET.get('month', None)
    project_id = request.GET.get('project', None)

    allocations = EmployeeResource.objects.all().select_related('employee', 'project_budget')

    if year and month:
        allocations = allocations.filter(
            project_budget__month=month,
            project_budget__year=year
        )
    
    if project_id:
        allocations = allocations.filter(project_budget__project__id=project_id)

    resource_allocations = {}
    for allocation in allocations:
        employee = allocation.employee
        if employee not in resource_allocations:
            resource_allocations[employee] = {
                'projects': [],
                'allocated': Decimal('0.0')
            }

        try:
            allocation_ratio = Decimal(allocation.allocation_ratio)
            resource_allocations[employee]['allocated'] += allocation_ratio
        except InvalidOperation:
            allocation_ratio = allocation.allocation_ratio

        resource_allocations[employee]['projects'].append({
            'project': allocation.project_budget.project.name,
            'allocation_ratio': allocation_ratio,
            'month': allocation.project_budget.month,
            'year': allocation.project_budget.year,
        })

    available_months = [month for month in list(calendar.month_abbr)[1:]]
    current_year = datetime.now().year
    available_years = [str(year) for year in range(current_year, current_year + 5)]

    available_projects = Project.objects.all()

    return render(request, 'resource_allocation_overview.html', {
        'resource_allocations': resource_allocations,
        'available_months': available_months,
        'available_years': available_years,
        'available_projects': available_projects,
        'selected_month': month,
        'selected_year': year,
        'selected_project': project_id,
    })

@login_required
def add_employee_resource(request, project_id):
    """Handle adding a new resource to a project."""
    project = get_object_or_404(Project, pk=project_id)

    selected_period = request.GET.get('period')
    try:
        month, year = selected_period.split()
    except (ValueError, AttributeError):
        messages.error(request, "Invalid or missing period information.")
        return redirect('project_details', project_id=project.id)

    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        allocation_ratio_input = request.POST.get('allocation_ratio').strip().lower()

        employee = get_object_or_404(User, pk=employee_id)

        allowed_values = ["0.1", "0.20", "0.25", "0.30", "0.40", "0.50", "0.60", "0.70", "0.75", "0.80", "0.90", "1.0", "intern"]

        if allocation_ratio_input not in allowed_values:
            messages.error(request, "Invalid allocation ratio. Please enter one of the allowed values.")
            return redirect('project_details', project_id=project.id)

        allocation_ratio = allocation_ratio_input if allocation_ratio_input == "intern" else float(allocation_ratio_input)

        budget = ProjectBudget.objects.filter(project=project, month=month, year=year).first()
        if budget:
            if allocation_ratio != "intern":
                current_allocations = EmployeeResource.objects.filter(
                    employee=employee, 
                    project_budget__month=month, 
                    project_budget__year=year
                ).aggregate(Sum('allocation_ratio'))['allocation_ratio__sum'] or 0

                if current_allocations + allocation_ratio > 1.0:
                    messages.error(request, "Allocation exceeds allowed limit for the employee in the selected period.")
                    return redirect('project_details', project_id=project.id)

            # Create the EmployeeResource
            EmployeeResource.objects.create(
                project_budget=budget,
                employee=employee,
                allocation_ratio=str(allocation_ratio) 
            )
            messages.success(request, "Resource added successfully.")
        else:
            messages.error(request, "No budget found for the selected period.")

    return redirect('project_details', project_id=project.id)

@login_required
def employee_overview(request):
    """View to display all employees."""
    employees = User.objects.filter(is_staff=False)  # Adjust as needed for your custom user fields
    return render(request, 'employee_overview.html', {'employees': employees})

@login_required
def add_employee(request):
    """View to add a new employee."""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee added successfully.")
            return redirect('employee_overview')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = EmployeeForm()

    return render(request, 'add_employee.html', {'form': form})

@login_required
def edit_employee(request, employee_id):
    """View to edit an employee's details."""
    employee = get_object_or_404(User, pk=employee_id)

    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated successfully.")
            return redirect('employee_overview')
    else:
        form = EmployeeForm(instance=employee)

    return render(request, 'edit_employee.html', {'form': form})

@login_required
def delete_employee(request, employee_id):
    """View to delete an employee."""
    employee = get_object_or_404(User, pk=employee_id)
    if request.method == 'POST':
        employee.delete()
        messages.success(request, "Employee deleted successfully.")
        return redirect('employee_overview')

    return render(request, 'delete_employee.html', {'employee': employee})

@login_required
def month_resource_allocation_overview(request):
    """View to display the sum of budgeted and actual resources for all projects in a specific month and year."""

    year = request.GET.get('year', None)
    month = request.GET.get('month', None)

    month_resource_summary = None
    if year and month:
        project_budgets = ProjectBudget.objects.filter(month=month, year=year)

        budgeted_resources_sum = project_budgets.aggregate(Sum('budgeted_resources'))['budgeted_resources__sum'] or Decimal('0.0')

        actual_resources_sum = EmployeeResource.objects.filter(project_budget__in=project_budgets).aggregate(
            total_allocation=Sum('allocation_ratio')
        )['total_allocation'] or Decimal('0.0')

        month_resource_summary = {
            'budgeted_resources_sum': budgeted_resources_sum,
            'actual_resources_sum': actual_resources_sum,
        }
    available_months = [month for month in list(calendar.month_abbr)[1:]]
    current_year = datetime.now().year
    available_years = [str(year) for year in range(current_year, current_year + 5)]

    return render(request, 'month_resource_allocation_overview.html', {
        'available_months': available_months,
        'available_years': available_years,
        'selected_month': month,
        'selected_year': year,
        'month_resource_summary': month_resource_summary,
    })

@login_required
def employee_management(request):
    return render(request, 'employee_management.html')
