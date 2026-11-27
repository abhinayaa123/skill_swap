
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.db.models import Q

from .models import SwapRequest
from .forms import SessionForm
from skills.models import Skill, UserSkill


@login_required
def send_swap_request(request, user_id, skill_id):

    # Prevent admins from sending swap requests
    if request.user.is_staff or request.user.is_superuser:
        messages.error(request, "Admins cannot send swap requests.")
        return redirect('admin_browse_skills')

    receiver = get_object_or_404(
    User,
    id=user_id,
    is_active=True )
    requested_skill = get_object_or_404(Skill, id=skill_id)

    if request.user == receiver:
        messages.error(request, "You cannot send a request to yourself.")
        return redirect('browse_skills')

    if request.method == "POST":
        offered_skill_id = request.POST.get('offered_skill')
        offered_skill = get_object_or_404(Skill, id=offered_skill_id)

        sender_offers_skill = UserSkill.objects.filter(
            user=request.user,
            skill__name__iexact=offered_skill.name,
            skill_type='TEACH'
        ).exists()

        sender_wants_skill = UserSkill.objects.filter(
            user=request.user,
            skill__name__iexact=requested_skill.name,
            skill_type='LEARN'
        ).exists()

        receiver_offers_skill = UserSkill.objects.filter(
            user=receiver,
            skill__name__iexact=requested_skill.name,
            skill_type='TEACH'
        ).exists()

        receiver_wants_skill = UserSkill.objects.filter(
            user=receiver,
            skill__name__iexact=offered_skill.name,
            skill_type='LEARN'
        ).exists()

        if not all([
            sender_offers_skill,
            sender_wants_skill,
            receiver_offers_skill,
            receiver_wants_skill
        ]):
            messages.error(request, "This is not a valid skill exchange.")
            return redirect('browse_skills')

        existing_request = SwapRequest.objects.filter(
            sender=request.user,
            receiver=receiver,
            requested_skill=requested_skill,
            offered_skill=offered_skill,
            status__in=['PENDING', 'ACCEPTED']
        ).exists()

        if existing_request:
            messages.error(request, "You have already sent this swap request.")
            return redirect('browse_skills')

        SwapRequest.objects.create(
            sender=request.user,
            receiver=receiver,
            requested_skill=requested_skill,
            offered_skill=offered_skill
        )

        messages.success(request, "Swap request sent successfully!")
        return redirect('browse_skills')

    offered_skills = UserSkill.objects.filter(
        user=request.user,
        skill_type='TEACH'
    ).select_related('skill')

    return render(request, 'swaps/send_request.html', {
        'receiver': receiver,
        'requested_skill': requested_skill,
        'offered_skills': offered_skills
    })

@login_required
def received_requests(request):
    requests = SwapRequest.objects.filter(
        receiver=request.user,
        status='PENDING'
    )

    return render(request, 'swaps/received_requests.html', {
        'requests': requests
    })


@login_required
@require_POST
def update_request_status(request, request_id, action):
    swap_request = get_object_or_404(
        SwapRequest,
        id=request_id,
        receiver=request.user,
        status='PENDING'
    )

    if action == 'accept':
        swap_request.status = 'ACCEPTED'
        messages.success(request, "Swap request accepted!")

    elif action == 'reject':
        swap_request.status = 'REJECTED'
        messages.success(request, "Swap request rejected!")
    else:
        messages.error(request, "Invalid request action.")
        return redirect('received_requests')
        
    swap_request.save()

    return redirect('received_requests')


@login_required
def my_swaps(request):
    swaps = SwapRequest.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user),
        status__in=['ACCEPTED', 'COMPLETED']
    )

    for item in swaps:
        item.user_has_reviewed = item.reviews.filter(
            reviewer=request.user
        ).exists()

    return render(request, 'swaps/my_swaps.html', {
        'swaps': swaps
    })


@login_required
def sent_requests(request):
    requests = SwapRequest.objects.filter(
        sender=request.user
    )

    return render(request, 'swaps/request_history.html', {
        'requests': requests
    })


@login_required
def cancel_request(request, request_id):
    if request.method == "POST":
        swap_request = get_object_or_404(
            SwapRequest,
            id=request_id,
            sender=request.user,
            status='PENDING'
        )

        swap_request.status = 'CANCELLED'
        swap_request.save()

        messages.success(request, "Swap request cancelled successfully!")

    return redirect('sent_requests')


@login_required
@require_POST
def confirm_completion(request, request_id):
    swap_request = get_object_or_404(
        SwapRequest,
        id=request_id,
        status='ACCEPTED'
    )
    if not swap_request.session_confirmed:
        messages.error(request, "The session must be confirmed before marking the exchange complete.")
        return redirect('my_swaps')

    if request.user == swap_request.sender:
        swap_request.sender_confirmed = True

    elif request.user == swap_request.receiver:
        swap_request.receiver_confirmed = True

    else:
        messages.error(request, "You are not part of this swap.")
        return redirect('my_swaps')

    if swap_request.sender_confirmed and swap_request.receiver_confirmed:
        swap_request.status = 'COMPLETED'
        messages.success(request, "Skill exchange completed successfully!")

    else:
        messages.success(request, "Your confirmation has been recorded.")

    swap_request.save()

    return redirect('my_swaps')


@login_required
def schedule_session(request, request_id):
    swap_request = get_object_or_404(
        SwapRequest,
        id=request_id,
        receiver=request.user,
        status='ACCEPTED'
    )

    if swap_request.session_confirmed:
        messages.error(
            request,
            "This session is already confirmed. You cannot change the schedule."
        )
        return redirect('my_swaps')

    if request.method == "POST":
        form = SessionForm(request.POST)

        if form.is_valid():
            swap_request.session_date = form.cleaned_data['session_date']
            swap_request.session_time = form.cleaned_data['session_time']
            swap_request.meeting_platform = form.cleaned_data['meeting_platform']
            swap_request.meeting_link = form.cleaned_data['meeting_link']

            swap_request.save()

            messages.success(request, "Session details saved successfully!")
            return redirect('my_swaps')

    else:
        form = SessionForm(initial={
            'session_date': swap_request.session_date,
            'session_time': swap_request.session_time,
            'meeting_platform': swap_request.meeting_platform,
            'meeting_link': swap_request.meeting_link,
        })

    return render(request, 'swaps/session_form.html', {
        'form': form,
        'swap_request': swap_request
    })

@login_required
@require_POST
def confirm_session(request, request_id):
    swap_request = get_object_or_404(
        SwapRequest,
        id=request_id,
        sender=request.user,
        status='ACCEPTED'
    )

    if not swap_request.session_date:
        messages.error(request, "No session has been scheduled yet.")
        return redirect('my_swaps')

    if swap_request.session_confirmed:
        messages.info(request, "Session is already confirmed.")
        return redirect('my_swaps')

    swap_request.session_confirmed = True
    swap_request.save()

    messages.success(request, "Session schedule confirmed successfully!")

    return redirect('my_swaps')