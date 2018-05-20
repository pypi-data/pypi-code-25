import markdown
import os
from prose_wc import wc
import pypandoc

from django.contrib.auth.models import User
from django.urls import reverse
from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


def original_file_path(instance, filename):
    return os.path.join(str(instance.call.id), '{}.{}'.format(
        instance.ctime.strftime('%Y-%m-%d-%H%M%S'),
        filename.split('.')[-1]))


class Call(models.Model):
    NOT_OPEN_YET = 1
    OPEN = 2
    CLOSED_REVIEWING = 3
    CLOSED_COMPLETED = 4
    CLOSED_FINAL = 5
    STATUS_CHOICES = (
        (NOT_OPEN_YET, 'Not open for submissions yet'),
        (OPEN, 'Open for submissions'),
        (CLOSED_REVIEWING, 'Closed for submissions, now reviewing'),
        (CLOSED_COMPLETED, 'Closed for submissions, reviewing completed'),
        (CLOSED_FINAL, 'Call completed'),
    )
    MAX_STATUS = CLOSED_FINAL

    owner = models.ForeignKey(
        User, related_name='submitify_calls_editing', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    status = models.PositiveIntegerField(choices=STATUS_CHOICES,
                                         default=NOT_OPEN_YET)
    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    end_date = models.DateField(blank=True, null=True)
    about_raw = models.TextField(verbose_name='about')
    about_rendered = models.TextField()
    paid = models.BooleanField(default=False)
    genre = models.CharField(max_length=50)
    length = models.CharField(max_length=50)
    reviews_per_submission = models.PositiveIntegerField(default=1)
    invite_only = models.BooleanField(default=False)
    readers = models.ManyToManyField(User,
                                     related_name='submitify_calls_reading')
    restricted_to = models.ManyToManyField(
        User, related_name='submitify_invitations')
    anonymous_submissions = models.BooleanField(default=True)
    readers_can_submit = models.BooleanField(default=False)

    def save(self):
        self.about_rendered = markdown.markdown(
            self.about_raw, extensions=['markdown.extensions.extra'])
        super(Call, self).save()

    def get_absolute_url(self):
        return reverse('submitify:view_call', kwargs={
            'call_id': self.id,
            'call_slug': slugify(self.title),
        })

    def get_next_status(self):
        try:
            return self.STATUS_CHOICES[self.status]
        except IndexError:
            return None

    def __str__(self):
        return self.title

    def __unicode__(self):
        return self.title


class Guideline(models.Model):
    DEFAULT_KEYS = (
        'Content restrictions',
        'Cover letter requirements',
        'Previous publication',
        'Multiple submissions',
        'Payment rate',
        'Payment via',
        'Publisher',
        'Contract information',
    )

    call = models.ForeignKey(Call, on_delete=models.CASCADE)
    key = models.CharField(max_length=100)
    value_raw = models.TextField()
    value_rendered = models.TextField()

    def save(self):
        self.value_rendered = markdown.markdown(
            self.value_raw, extensions=['markdown.extensions.extra'])
        super(Guideline, self).save()


class Submission(models.Model):
    SUBMITTED = 's'
    IN_REVIEW = 'i'
    REVIEWED = 'c'
    ACCEPTED = 'a'
    REJECTED = 'r'
    STATUS_CHOICES = (
        (SUBMITTED, 'Submitted'),
        (IN_REVIEW, 'Needs reviews'),
        (REVIEWED, 'Requested reviews completed'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    )

    owner = models.ForeignKey(
        User, related_name='submitify_submissions', on_delete=models.CASCADE)
    call = models.ForeignKey(
        Call, related_name='submitify_submissions', on_delete=models.CASCADE)

    # Basics
    title = models.CharField(max_length=200)
    cover = models.TextField()

    # Originally submitted file
    original_file = models.FileField(upload_to=original_file_path)

    # Rendered to manuscript format
    submission_file = models.FileField()

    # Rendered from plain markdown
    submission_text = models.TextField()

    # Other data
    ctime = models.DateTimeField(auto_now_add=True)
    wordcount = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=1, choices=STATUS_CHOICES,
                              default=SUBMITTED)

    def save(self, *args, **kwargs):
        self.ctime = timezone.now()
        self.cover = markdown.markdown(
            self.cover, extensions=['markdown.extensions.extra'])
        process_file = (kwargs.pop('process_file')
                        if 'process_file' in kwargs else False)
        if process_file:
            self.submission_text = markdown.markdown(
                pypandoc.convert_file(self.original_file.path, 'md'))
            self.wordcount = wc.wc(
                None, pypandoc.convert(
                    self.submission_text, 'plain', 'html'))['counts']['words']
        super(Submission, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('submitify:view_submission', kwargs={
            'call_id': self.call.id,
            'call_slug': slugify(self.call.title),
            'submission_id': self.id,
        })

    def get_class_for_status(self):
        return {
            Submission.SUBMITTED: '',
            Submission.IN_REVIEW: 'info',
            Submission.REVIEWED: 'info',
            Submission.ACCEPTED: 'success',
            Submission.REJECTED: 'danger',
        }[self.status]

    def get_review_stats(self):
        reviews = self.submitify_reviews.all()
        if len(reviews) == 0:
            return {
                'total': 0,
                'accept': 0,
                'reject': 0,
                'average_rating': 0
            }
        return {
            'total': len(reviews),
            'accept': len(list(filter(lambda x: x.yea_nay == 'a', reviews))),
            'reject': len(list(filter(lambda x: x.yea_nay == 'r', reviews))),
            'average_rating':
                sum([r.rating for r in reviews]) / len(reviews),
        }


class Review(models.Model):
    ACCEPT = 'a'
    REJECT = 'r'
    STATUS_CHOICES = (
        (ACCEPT, 'Accept'),
        (REJECT, 'Reject'),
    )

    owner = models.ForeignKey(
        User, related_name='submitify_reviews', on_delete=models.CASCADE)
    submission = models.ForeignKey(
        Submission, related_name='submitify_reviews', on_delete=models.CASCADE)
    ctime = models.DateTimeField(auto_now_add=True)
    mtime = models.DateTimeField(auto_now=True)
    rating = models.PositiveIntegerField()
    yea_nay = models.CharField(max_length=1, blank=True,
                               choices=STATUS_CHOICES,
                               verbose_name="accept or reject")
    comments_raw = models.TextField(verbose_name="review comments")
    comments_rendered = models.TextField()

    def save(self):
        self.comments_rendered = markdown.markdown(
            self.comments_raw, extensions=['markdown.extensions.extra'])
        super(Review, self).save()

    def get_absolute_url(self):
        return reverse('submitify:view_review', kwargs={
            'call_id': self.submission.call.id,
            'call_slug': slugify(self.submission.call.title),
            'submission_id': self.submission.id,
            'review_id': self.id,
        })


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('b', 'Basic notification'),
        ('a', 'Notification for accepted authors'),
        ('r', 'Notification for rejected authors'),
    )

    call = models.ForeignKey(
        Call, related_name='submitify_notifications', on_delete=models.CASCADE)
    targets = models.ManyToManyField(User,
                                     related_name='submitify_notifications')
    notification_type = models.CharField(max_length=1,
                                         choices=NOTIFICATION_TYPES)
    ctime = models.DateTimeField(auto_now_add=True)
    subject = models.CharField(max_length=100)
    body_raw = models.TextField()
    body_rendered = models.TextField()

    def save(self):
        self.body_rendered = markdown.markdown(
            self.body_raw, extensions=['markdown.extensions.extra'])
        super(Notification, self).save()
        # TODO send email

    def get_absolute_url(self):
        return reverse('submitify:view_notification', kwargs={
            'call_id': self.call.id,
            'call_slug': slugify(self.call.title),
            'notification_id': self.id,
        })
