from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from swaps.models import SwapRequest
from .models import Review
from .forms import ReviewForm




@login_required
def add_review(request, swap_id):

    swap = get_object_or_404(
        SwapRequest,
        id=swap_id,
        status='COMPLETED'
    )

    if request.user not in [swap.sender, swap.receiver]:
        messages.error(request, "You are not part of this swap.")
        return redirect('my_swaps')

    if request.method == "POST":

        form = ReviewForm(request.POST)

        if form.is_valid():

            reviewed_user = (
                swap.receiver
                if request.user == swap.sender
                else swap.sender
            )

            if Review.objects.filter(
                swap=swap,
                reviewer=request.user
            ).exists():
                messages.error(request, "You have already reviewed this swap.")
                return redirect('my_swaps')

            review = form.save(commit=False)
            review.swap = swap
            review.reviewer = request.user
            review.reviewed_user = reviewed_user
            review.save()

            messages.success(request, "Review submitted successfully!")
            return redirect('my_swaps')

    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {
        'form': form,
        'swap': swap
    })