
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import UserSkillForm
from .models import Skill, SkillCategory, UserSkill
from reviews.models import Review
from django.db.models import Avg



@login_required
def add_skill(request):

    if request.method == "POST":
        form = UserSkillForm(request.POST)

        if form.is_valid():

            skill_name = form.cleaned_data['skill']
            category_name = form.cleaned_data['category']
            skill_type = form.cleaned_data['skill_type']

            category, created = SkillCategory.objects.get_or_create(
                name=category_name
            )

            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                category=category
            )

            UserSkill.objects.get_or_create(
                user=request.user,
                skill=skill,
                skill_type=skill_type
            )

            return redirect('profile')

    else:
        form = UserSkillForm()

    return render(request, 'skills/add_skill.html', {'form': form})


@login_required
def edit_skill(request, skill_id):

    user_skill = get_object_or_404(
        UserSkill,
        id=skill_id,
        user=request.user
    )

    if request.method == "POST":
        form = UserSkillForm(request.POST)

        if form.is_valid():

            skill_name = form.cleaned_data['skill']
            category_name = form.cleaned_data['category']
            skill_type = form.cleaned_data['skill_type']

            category, created = SkillCategory.objects.get_or_create(
                name=category_name
            )

            skill, created = Skill.objects.get_or_create(
                name=skill_name,
                category=category
            )

            user_skill.skill = skill
            user_skill.skill_type = skill_type
            user_skill.save()

            return redirect('profile')

    else:
        form = UserSkillForm(initial={
            'skill': user_skill.skill.name,
            'category': user_skill.skill.category.name if user_skill.skill.category else '',
            'skill_type': user_skill.skill_type
        })

    return render(
        request,
        'skills/edit_skill.html',
        {'form': form, 'user_skill': user_skill}
    )




@login_required
def browse_skills(request):

    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_browse_skills')

    learn_query = request.GET.get('learn', '').strip()
    teach_query = request.GET.get('teach', '').strip()

    # Display all teaching skills by default
    skills = UserSkill.objects.filter(
        skill_type='TEACH',
        user__is_active=True
    ).exclude(
        user=request.user
    ).select_related(
        'user', 'skill', 'skill__category'
    )

    # Apply two-way matching when both fields are entered
    if learn_query and teach_query:

        matching_users = UserSkill.objects.filter(
            skill_type='LEARN',
            skill__name__icontains=teach_query,
            user__is_active=True
        ).values_list('user_id', flat=True)

        skills = skills.filter(
            skill__name__icontains=learn_query,
            user_id__in=matching_users
        )

    for item in skills:

        user_reviews = Review.objects.filter(
            reviewed_user=item.user
        )

        item.average_rating = user_reviews.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']

        item.total_reviews = user_reviews.count()

    return render(
        request,
        'skills/browse_skills.html',
        {
            'skills': skills,
            'learn_query': learn_query,
            'teach_query': teach_query
        }
    )

def guest_browse_skills(request):

    # Redirect logged-in users to their respective browse pages
    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_browse_skills')
        return redirect('browse_skills')

    learn_query = request.GET.get('learn', '').strip()
    teach_query = request.GET.get('teach', '').strip()

    skills = UserSkill.objects.filter(
        skill_type='TEACH',
        user__is_active=True
    ).select_related(
        'user', 'skill', 'skill__category'
    )

    # Apply two-way matching when both fields are entered
    if learn_query and teach_query:

        matching_users = UserSkill.objects.filter(
            skill_type='LEARN',
            skill__name__iexact=teach_query,
            user__is_active=True
        ).values_list('user_id', flat=True)

        skills = skills.filter(
            skill__name__iexact=learn_query,
            user_id__in=matching_users
        )

    # Calculate ratings for each teacher
    for item in skills:
        user_reviews = Review.objects.filter(
            reviewed_user=item.user
        )

        item.average_rating = user_reviews.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']

        item.total_reviews = user_reviews.count()

    return render(
        request,
        'skills/browse_skills.html',
        {
            'skills': skills,
            'learn_query': learn_query,
            'teach_query': teach_query
        }
    )



@login_required
def admin_browse_skills(request):

    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('user_home')
 
    search_query = request.GET.get('search', '').strip()

    skills = UserSkill.objects.filter(
        skill_type='TEACH',
        user__is_active=True
    ).select_related(
        'user', 'skill', 'skill__category'
    )

    if search_query:
        skills = skills.filter(
            skill__name__icontains=search_query
        )

    for item in skills:
        user_reviews = Review.objects.filter(
            reviewed_user=item.user
        )

        item.average_rating = user_reviews.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating']

        item.total_reviews = user_reviews.count()

    return render(
        request,
        'skills/admin_browse_skill.html',
        {
            'skills': skills,
            'search_query': search_query
        }
    )
