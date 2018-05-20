import magic
import os
import pypandoc
import shutil
import subprocess
import tempfile

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from submitify.forms import (
    ReviewForm,
    SubmissionForm,
)
from submitify.models import (
    Call,
    Notification,
    Review,
    Submission,
)


def manuscriptify(instance):
    # TODO move to models
    tempdir = tempfile.mkdtemp()
    contents = pypandoc.convert_file(instance.original_file.path, 'latex')
    rendered = render_to_string('submitify/manuscript.tex', context={
        'call': instance.call.title,
        'title': instance.title,
        'contents': contents,
    })
    with open(os.path.join(tempdir, 'manuscript.tex'), 'w') as f:
        f.write(rendered)
    subprocess.call([
        'pdflatex',
        '-output-directory',
        tempdir,
        os.path.join(tempdir, 'manuscript.tex')
    ])
    file_dir = os.path.dirname(os.path.abspath(instance.original_file.path))
    with open(os.path.join(tempdir, 'manuscript.pdf'), 'rb') as outfile:
        instance.submission_file.save(
            os.path.join(file_dir, '{}.pdf'.format(instance.id)),
            outfile,
            save=False)
    shutil.rmtree(tempdir, True)


@login_required
@require_POST
def create_submission(request, call_id=None, call_slug=None):
    call = get_object_or_404(Call, pk=call_id)
    if call.status != Call.OPEN:
        messages.error(request, 'This call is not open for submissions')
        return redirect(call.get_absolute_url())
    elif (call.invite_only and request.user not in call.restricted_to.all()):
        messages.error(request, 'This call is invite-only')
        return redirect(call.get_absolute_url())
    elif (not call.readers_can_submit and request.user in call.readers.all()):
        messages.error(request, 'This call is not open for submissions by '
                       'readers for the call')
        return redirect(call.get_absolute_url())
    form = SubmissionForm(request.POST, request.FILES)
    if form.is_valid():
        submission = form.save(commit=False)
        submission.call = call
        submission.owner = request.user
        submission.save()
        form.save_m2m()
        manuscriptify(submission)
        submission.save(process_file=True)
        messages.success(request, 'Work submitted!')
        return redirect(call.get_absolute_url())
    notifications = Notification.objects.filter(
        call=call, targets__in=[request.user])
    return render(request, 'submitify/calls/view.html', {
        'title': call.title,
        'subtitle': call.get_status_display(),
        'call': call,
        'can_submit': True,
        'form': form,
        'with_submissions': request.user in call.readers.all(),
        'notifications': notifications,
    })


@login_required
def view_submission(request, call_id=None, call_slug=None,
                    submission_id=None):
    call = get_object_or_404(Call, pk=call_id)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    if not (request.user in call.readers.all() or request.user == call.owner):
        messages.error(request, "Only users listed as that call's readers "
                       "may view submissions for that call.")
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    can_review = True
    if call.status < Call.OPEN or call.status > Call.CLOSED_REVIEWING:
        can_review = False
    elif submission.status in [Submission.ACCEPTED, Submission.REJECTED]:
        can_review = False
    if can_review:
        try:
            review = Review.objects.get(submission=submission,
                                        owner=request.user)
        except Review.DoesNotExist:
            review = None
        form = ReviewForm(instance=review)
        if request.method == 'POST':
            form = ReviewForm(request.POST, instance=review)
            if form.is_valid():
                review = form.save(commit=False)
                review.owner = request.user
                review.submission = submission
                review.save()
                form.save_m2m()
                return redirect(submission.get_absolute_url())
    else:
        form = None
        review = None
    return render(request, 'submitify/submissions/view.html', {
        'title': 'Submission <em>{}</em>'.format(submission.title),
        'subtitle': '{} for <em>{}</em>'.format(
            submission.get_status_display(), call.title),
        'call': call,
        'form': form,
        'review': review,
        'submission': submission,
        'can_review': can_review,
    })


@login_required
def view_submission_text(request, call_id=None, call_slug=None,
                         submission_id=None):
    call = get_object_or_404(Call, pk=call_id)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    if not (request.user in call.readers.all() or request.user == call.owner):
        messages.error(request, "Only users listed as that call's readers "
                       "may view submissions for that call.")
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    return render(request, 'submitify/submissions/view_text.html', {
        'submission': submission,
    })


@login_required
def view_submission_file(request, call_id=None, call_slug=None,
                         submission_id=None):
    call = get_object_or_404(Call, pk=call_id)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    if not (request.user in call.readers.all() or request.user == call.owner):
        messages.error(request, "Only users listed as that call's readers "
                       "may view submissions for that call.")
        return render(request, 'permission_denied.html', {}, status=403)
    contents = submission.submission_file.read()
    return HttpResponse(contents, content_type='application/pdf')


@login_required
def view_original_file(request, call_id=None, call_slug=None,
                       submission_id=None):
    call = get_object_or_404(Call, pk=call_id)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    if not (request.user in call.readers.all() or request.user == call.owner):
        messages.error(request, "Only users listed as that call's readers "
                       "may view submissions for that call.")
        return render(request, 'permission_denied.html', {}, status=403)
    contents = submission.original_file.read()
    mime = magic.Magic(mime=True)
    return HttpResponse(contents, content_type=mime.from_file(
        submission.original_file.path))


@login_required
def resolve_submission(request, call_id=None, call_slug=None,
                       submission_id=None, resolution_type=None):
    call = get_object_or_404(Call, pk=call_id)
    if request.user != call.owner:
        messages.error(request, "Only the owner of the call "
                       "may resolve submissions for that call.")
        return render(request, 'permission_denied.html', {}, status=403)
    if call.status < Call.CLOSED_REVIEWING:
        messages.error(request, 'You may only {} submissions when '
                       'reviewing is completed'.format(resolution_type))
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    submission = get_object_or_404(Submission, pk=submission_id, call=call)
    submission.status = resolution_type[0]
    submission.save()
    return redirect(submission.get_absolute_url())
