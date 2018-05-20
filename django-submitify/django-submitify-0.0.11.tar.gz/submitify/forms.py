from django import forms
from django.contrib.auth.models import User

from .models import (
    Call,
    Guideline,
    Notification,
    Review,
    Submission,
)


class CallForm(forms.ModelForm):
    class Meta:
        model = Call
        fields = [
            'title',
            'paid',
            'genre',
            'length',
            'end_date',
            'about_raw',
            'reviews_per_submission',
            'anonymous_submissions',
            'readers_can_submit',
            'invite_only',
        ]


class GuidelineForm(forms.ModelForm):
    DEFAULT_KEYS = Guideline.DEFAULT_KEYS

    class Meta:
        model = Guideline
        fields = ['key', 'value_raw']


GuidelineFormset = forms.formset_factory(GuidelineForm)


class InviteForm(forms.Form):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.HiddenInput())
    calls = forms.ModelChoiceField(
        queryset=Call.objects.all())


class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ['subject', 'body_raw']
        widgets = {
            'notification_type': forms.HiddenInput(),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'yea_nay', 'comments_raw']


class SubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ['title', 'cover', 'original_file']
