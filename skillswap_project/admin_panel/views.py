from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from skills.models import Skill, UserSkill
def is_admin(user):
    return user.is_staff or user.is_superuser 


@login_required
@user_passes_test(is_admin)
def dashboard(request):
    return render(request, 'admin_panel/admin_dashboard.html') 

@login_required
@user_passes_test(is_admin)
def manage_users(request):
    users = User.objects.filter(
    is_superuser=False,
    is_staff=False
    ).order_by('-date_joined')

    return render(
        request,
        'admin_panel/manage_users.html',
        {'users': users}
    )
@login_required
@user_passes_test(is_admin)
@require_POST
def toggle_user_status(request, user_id):

    user = get_object_or_404(
        User,
        id=user_id,
        is_superuser=False,
        is_staff=False
    )

    user.is_active = not user.is_active
    user.save()

    return redirect('manage_users')

@login_required
@user_passes_test(is_admin)
def manage_skills(request):

    skills = UserSkill.objects.select_related(
        'user',
        'skill',
        'skill__category'
    ).order_by('skill__name')

    return render(
        request,
        'admin_panel/manage_skills.html',
        {'skills': skills}
    )

@login_required
@user_passes_test(is_admin)
@require_POST
def delete_user_skill(request, skill_id):

    user_skill = get_object_or_404(
        UserSkill,
        id=skill_id
    )

    user_skill.delete()

    return redirect('manage_skills')



