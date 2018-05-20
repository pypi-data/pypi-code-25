from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from submitify.forms import NotificationForm
from submitify.models import (
    Call,
    Notification,
    Submission,
)


@login_required
def view_notification(request, call_id=None, call_slug=None,
                      notification_id=None):
    call = get_object_or_404(Call, pk=call_id)
    notification = get_object_or_404(Notification, pk=notification_id,
                                     call=call)
    if not (request.user == call.owner or
            request.user in notification.targets.all()):
        messages.error(request, 'Only the call owner or notified individuals '
                       'may view this notification')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    return render(request, 'submitify/notifications/view.html', {
        'title': 'Author notification',
        'subtitle': notification.get_notification_type_display(),
        'call': call,
        'notification': notification,
    })


@login_required
def send_notification(request, call_id=None, call_slug=None,
                      notification_type=None):
    call = get_object_or_404(Call, pk=call_id)
    if request.user != call.owner:
        messages.error(request, 'Only the call owner may send notifications')
        return render(request, 'submitify/permission_denied.html', {},
                      status=403)
    if (call.status < Call.CLOSED_COMPLETED and
            notification_type in ['accept', 'reject']):
        messages.error(request, 'You may not notify users of acceptance or '
                       'rejection unless the call is closed and completed')
        return redirect(call.get_absolute_url())
    form = NotificationForm()
    if request.method == 'POST':
        form = NotificationForm(request.POST)
        if form.is_valid():
            notification = form.save(commit=False)
            notification.call = call
            notification.notification_type = notification_type[0]
            submissions = call.submitify_submissions.all()
            if notification_type == 'accept':
                submissions = submissions.filter(status=Submission.ACCEPTED)
            if notification_type == 'reject':
                submissions = submissions.filter(status=Submission.REJECTED)
            notification.save()
            form.save_m2m()
            targets = [s.owner for s in submissions]
            for target in targets:
                notification.targets.add(target)
            return redirect(notification.get_absolute_url())
    return render(request, 'submitify/notifications/create.html', {
        'title': 'Send notification',
        'subtitle': Notification(
            notification_type=notification_type[0]
        ).get_notification_type_display(),
        'call': call,
        'form': form,
        'notification_type': notification_type,
    })
