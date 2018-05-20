from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from submitify.forms import ReviewForm
from submitify.models import (
    Call,
    Review,
    Submission
)


@login_required
def create_review(request, call_id=None, call_slug=None, submission_id=None):
    call = get_object_or_404(Call, pk=call_id)
    if not (request.user in call.readers.all() or request.user == call.owner):
        messages.error(request, 'Only readers for this call may view '
                       'submission reviews')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    form = ReviewForm()
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.owner = request.user
            review.submission = submission
            review.save()
            form.save_m2m()
            review_count = submission.submitify_reviews.count()
            if review_count == 1:
                submission.status = Submission.IN_REVIEW
            if review_count >= call.reviews_per_submission:
                submission.status = Submission.REVIEWED
            submission.save()
            return redirect(review.get_absolute_url())
    return render(request, 'submitify/reviews/create.html', {
        'call': call,
        'submission': submission,
        'form': form,
    })


@login_required
def view_review(request, call_id=None, call_slug=None, submission_id=None,
                review_id=None):
    call = get_object_or_404(Call, pk=call_id)
    if not (request.user in call.readers.all() or request.user == call.owner):
        messages.error(request, 'Only readers for this call may view '
                       'submission reviews')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    review = get_object_or_404(Review, pk=review_id, submission=submission)
    if request.user not in [review.owner, call.owner]:
        messages.error(request, 'Only readers for this call may view '
                       'submission reviews')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    return render(request, 'submitify/reviews/view.html', {
        'title': "{}'s review of <em>{}</em>".format(review.owner.username,
                                                     submission.title),
        'subtitle': 'For <em>{}</em>'.format(call.title),
        'call': call,
        'submission': submission,
        'review': review,
    })


@login_required
def edit_review(request, call_id=None, call_slug=None, submission_id=None,
                review_id=None):
    call = get_object_or_404(Call, pk=call_id)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    review = get_object_or_404(Review, pk=review_id, submission=submission)
    if request.user != review.owner:
        messages.error(request, 'Only the reviewer may edit their review')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    form = ReviewForm(instance=review)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            review = form.save()
            return redirect(review.get_absolute_url())
    return render(request, 'submitify/reviews/create.html', {
        'call': call,
        'submission': submission,
        'form': form,
    })
