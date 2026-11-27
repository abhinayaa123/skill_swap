
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.views.decorators.http import require_POST
from django.db import transaction, IntegrityError
from django.db.models import Avg

from .models import Profile
from .forms import ProfileForm

from skills.models import UserSkill
from reviews.models import Review


# USER REGISTRATION
def register_view(request):

    if request.user.is_authenticated:
        if request.user.is_staff or request.user.is_superuser:
            return redirect("admin_dashboard")
        return redirect("user_home")

    if request.method == "POST":

        full_name = request.POST.get("full_name", "").strip()
        email = request.POST.get("email", "").strip()
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        context = {
            "full_name": full_name,
            "email": email,
            "username": username,
        }

        # Check required fields
        if not all([full_name, email, username, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return render(request, "accounts/register.html", context)

        # Validate email
        try:
            validate_email(email)
        except ValidationError:
            messages.error(request, "Enter a valid email address.")
            return render(request, "accounts/register.html", context)

        # Check password matching
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "accounts/register.html", context)

        # Check duplicate username
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username already taken.")
            return render(request, "accounts/register.html", context)

        # Check duplicate email
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, "Email already registered.")
            return render(request, "accounts/register.html", context)

        # Split full name
        name_parts = full_name.split(maxsplit=1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        # Prepare user for password validation
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        # Validate password
        try:
            validate_password(password, user=user)
        except ValidationError as error:
            for message in error.messages:
                messages.error(request, message)

            return render(request, "accounts/register.html", context)

        # Create user and profile safely
        try:
            with transaction.atomic():

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name
                )

                Profile.objects.create(user=user)

        except IntegrityError:
            messages.error(
                request,
                "Registration failed. This username may already exist."
            )
            return render(request, "accounts/register.html", context)

    
        messages.success(request, "Registration successful!")
        return redirect("user_home")

    return render(request, "accounts/register.html")


# USER HOME
@login_required
def user_home(request):

    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')

    return render(request, 'accounts/user_home.html')


# USER LOGIN
def user_login(request):

    if request.user.is_authenticated:

        if request.user.is_staff or request.user.is_superuser:
            return redirect("admin_dashboard")

        return redirect("user_home")

    if request.method == "POST":

        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:

            login(request, user)

            if user.is_staff or user.is_superuser:
                return redirect("admin_dashboard")

            return redirect("user_home")

        messages.error(request, "Invalid username or password.")
        return redirect("user_login")

    return render(request, "accounts/login.html")


# USER LOGOUT
@require_POST
def user_logout(request):

    logout(request)

    messages.success(request, "You have logged out successfully.")

    return redirect("user_login")


# USER PROFILE
@login_required
def profile(request):

    user_profile = Profile.objects.filter(
        user=request.user
    ).first()

    skills_to_teach = UserSkill.objects.filter(
        user=request.user,
        skill_type='TEACH'
    )

    skills_to_learn = UserSkill.objects.filter(
        user=request.user,
        skill_type='LEARN'
    )

    reviews = Review.objects.filter(
        reviewed_user=request.user
    ).select_related('reviewer').order_by('-created_at')

    average_rating = reviews.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating']

    total_reviews = reviews.count()

    context = {
        'profile': user_profile,
        'skills_to_teach': skills_to_teach,
        'skills_to_learn': skills_to_learn,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
    }

    return render(request, 'accounts/profile.html', context)


# DELETE ACCOUNT
@login_required
def delete_account(request):

    if request.method == 'POST':
        user = request.user
        user.is_active = False
        user.save()

        logout(request)

        return redirect('user_login')

    return render(request, 'accounts/delete_account.html')


# MY REVIEWS
@login_required
def my_reviews(request):

    reviews = Review.objects.filter(
        reviewed_user=request.user
    ).select_related('reviewer').order_by('-created_at')

    average_rating = reviews.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating']

    total_reviews = reviews.count()

    context = {
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
    }

    return render(request, 'accounts/my_reviews.html', context)


# EDIT PROFILE
@login_required
def edit_profile(request):

    profile, created = Profile.objects.get_or_create(
        user=request.user
    )

    if request.method == "POST":

        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile updated successfully!"
            )

            return redirect("profile")

    else:
        form = ProfileForm(instance=profile)

    return render(
        request,
        "accounts/profile_form.html",
        {"form": form}
    )


# VIEW OTHER USER PROFILE
@login_required
def view_user_profile(request, user_id):

    viewed_user = get_object_or_404(User, id=user_id)

    user_profile = Profile.objects.filter(
        user=viewed_user
    ).first()

    skills_to_teach = UserSkill.objects.filter(
        user=viewed_user,
        skill_type='TEACH'
    )

    skills_to_learn = UserSkill.objects.filter(
        user=viewed_user,
        skill_type='LEARN'
    )

    # Fetch public reviews
    reviews = Review.objects.filter(
        reviewed_user=viewed_user
    ).select_related('reviewer').order_by('-created_at')

    # Calculate average rating
    average_rating = reviews.aggregate(
        avg_rating=Avg('rating')
    )['avg_rating']

    # Count total reviews
    total_reviews = reviews.count()

    # Prepare context
    context = {
        'viewed_user': viewed_user,
        'profile': user_profile,
        'skills_to_teach': skills_to_teach,
        'skills_to_learn': skills_to_learn,
        'reviews': reviews,
        'average_rating': average_rating,
        'total_reviews': total_reviews,
    }

    return render(
        request,
        'accounts/view_user_profile.html',
        context
    )


# GUEST HOME
def guest_home(request):

    if request.user.is_authenticated:

        if request.user.is_staff or request.user.is_superuser:
            return redirect('admin_dashboard')

        return redirect('user_home')

    return render(request, 'home.html')
