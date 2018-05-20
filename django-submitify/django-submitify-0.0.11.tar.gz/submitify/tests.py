import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth.models import User
from django.test import (
    TestCase as TC,
    override_settings,
)

from .models import (
    Call,
    Guideline,
    Notification,
    Review,
    Submission,
    original_file_path,
)


@override_settings(MEDIA_ROOT=tempfile.mkdtemp())
class TestCase(TC):
    @classmethod
    def tearDownModule(cls):
        shutil.rmtree(settings.MEDIA_ROOT, True)


class UserMixin(object):
    @classmethod
    def setUpTestData(cls):
        # We can't use get_or_create because we need to use
        # User.objects.create_user rather than just create.
        try:
            cls.owner = User.objects.get(username='owner')
        except User.DoesNotExist:
            cls.owner = User.objects.create_user(
                'owner',
                'owner@example.com',
                'owner pass')
            cls.owner.is_superuser = True
            cls.owner.is_staff = True
            cls.owner.save()

        try:
            cls.reader = User.objects.get(username='reader')
        except User.DoesNotExist:
            cls.reader = User.objects.create_user(
                'reader',
                'reader@example.com',
                'reader pass')
            cls.reader.save()

        try:
            cls.writer = User.objects.get(username='writer')
        except User.DoesNotExist:
            cls.writer = User.objects.create_user(
                'writer',
                'writer@example.com',
                'writer pass')
            cls.writer.save()


class CallMixin(UserMixin):
    @classmethod
    def setUpTestData(cls):
        super(CallMixin, cls).setUpTestData()
        cls.call = Call(
            owner=cls.owner,
            status=Call.OPEN,
            title='Test call for submissions',
            about_raw='Testing',
            genre='test',
            length='1000-5000')
        cls.call.save()
        cls.call.readers.add(cls.reader)


class GuidelineMixin(CallMixin):
    @classmethod
    def setUpTestData(cls):
        super(GuidelineMixin, cls).setUpTestData()
        cls.guideline = Guideline(
            call=cls.call,
            key='Test key',
            value_raw='Test value')
        cls.guideline.save()


class SubmissionMixin(CallMixin):
    @classmethod
    def setUpTestData(cls):
        super(SubmissionMixin, cls).setUpTestData()
        cls.file_contents = b'# My great story\n\nFoxes are great.\n\nThe end.'
        with open(os.path.join(settings.MEDIA_ROOT, 'in.md'), 'wb') as f:
            f.write(cls.file_contents)
        with open(os.path.join(settings.MEDIA_ROOT, 'out.pdf'), 'wb') as f:
            f.write(cls.file_contents)
        cls.submission = Submission(
            owner=cls.writer,
            call=cls.call,
            title='Test submission',
            cover='This is a *great* work by *me*',
            original_file=os.path.join(settings.MEDIA_ROOT, 'in.md'),
            submission_file=os.path.join(settings.MEDIA_ROOT, 'out.pdf'))
        cls.submission.save(process_file=True)


class NotificationMixin(SubmissionMixin):
    @classmethod
    def setUpTestData(cls):
        super(NotificationMixin, cls).setUpTestData()
        cls.notification = Notification(
            call=cls.call,
            notification_type='b',
            subject='Test notification',
            body_raw="I'm working on it, *don't rush me*")
        cls.notification.save()
        cls.notification.targets.add(cls.writer)


class ReviewMixin(SubmissionMixin):
    @classmethod
    def setUpTestData(cls):
        super(ReviewMixin, cls).setUpTestData()
        cls.review = Review(
            owner=cls.reader,
            submission=cls.submission,
            rating=4,
            yea_nay=Review.ACCEPT,
            comments_raw='It was **okay** I guess')
        cls.review.save()


class CallModelTest(CallMixin, TestCase):
    def test_save(self):
        self.call.about_raw = 'Testing **markdown**'
        self.call.save()
        self.assertEqual(self.call.about_rendered,
                         '<p>Testing <strong>markdown</strong></p>')

    def test_get_absolute_url(self):
        self.assertEqual(self.call.get_absolute_url(),
                         '/1-test-call-for-submissions/')

    def test_get_next_status(self):
        self.call.status = Call.NOT_OPEN_YET
        self.assertEqual(self.call.get_next_status(),
                         Call.STATUS_CHOICES[Call.NOT_OPEN_YET])
        self.call.status = Call.OPEN
        self.assertEqual(self.call.get_next_status(),
                         Call.STATUS_CHOICES[Call.OPEN])
        self.call.status = Call.CLOSED_REVIEWING
        self.assertEqual(self.call.get_next_status(),
                         Call.STATUS_CHOICES[Call.CLOSED_REVIEWING])
        self.call.status = Call.CLOSED_COMPLETED
        self.assertEqual(self.call.get_next_status(),
                         Call.STATUS_CHOICES[Call.CLOSED_COMPLETED])
        self.call.status = Call.CLOSED_FINAL
        self.assertEqual(self.call.get_next_status(), None)

    def test_repr(self):
        self.assertEqual(self.call.__str__(), self.call.title)
        self.assertEqual(self.call.__unicode__(), self.call.title)


class GuidelineModelTest(GuidelineMixin, TestCase):
    def test_save(self):
        self.guideline.value_raw = 'Testing **markdown**'
        self.guideline.save()
        self.assertEqual(self.guideline.value_rendered,
                         '<p>Testing <strong>markdown</strong></p>')


class SubmissionModelTest(SubmissionMixin, TestCase):
    def test_original_file_path(self):
        self.assertEqual(original_file_path(self.submission, 'foo.md'),
                         '1/{}.md'.format(self.submission.ctime.strftime(
                              '%Y-%m-%d-%H%M%S')))

    def test_save(self):
        self.assertEqual(self.submission.cover,
                         '<p>This is a <em>great</em> work by <em>me</em></p>')
        self.assertIn('<p>Foxes are great.</p>',
                      self.submission.submission_text)

    def test_get_absolute_url(self):
        self.assertEqual(self.submission.get_absolute_url(),
                         '/1-test-call-for-submissions/1/')

    def test_get_class_for_status(self):
        results = []
        for status in [i[0] for i in Submission.STATUS_CHOICES]:
            self.submission.status = status
            results.append(self.submission.get_class_for_status())
        self.assertEqual(results, [
            '',
            'info',
            'info',
            'success',
            'danger',
        ])

    def test_get_review_stats_empty(self):
        self.assertEqual(self.submission.get_review_stats(), {
            'total': 0,
            'accept': 0,
            'reject': 0,
            'average_rating': 0,
        })

    def test_get_review_stats_with_reviews(self):
        Review(
            owner=self.reader,
            submission=self.submission,
            rating=5,
            yea_nay=Review.ACCEPT,
            comments_raw='Good').save()
        Review(
            owner=self.owner,
            submission=self.submission,
            rating=1,
            yea_nay=Review.REJECT,
            comments_raw='Bad').save()
        self.assertEqual(self.submission.get_review_stats(), {
            'total': 2,
            'accept': 1,
            'reject': 1,
            'average_rating': 3.0,
        })


class ReviewModelTest(ReviewMixin, TestCase):
    def test_save(self):
        self.assertEqual(self.review.comments_rendered,
                         '<p>It was <strong>okay</strong> I guess</p>')

    def test_get_absolute_url(self):
        self.assertEqual(self.review.get_absolute_url(),
                         '/1-test-call-for-submissions/1/reviews/1/')


class NotificationModelTest(NotificationMixin, TestCase):
    def test_save(self):
        self.assertEqual(self.notification.body_rendered,
                         "<p>I'm working on it, <em>don't rush me</em></p>")

    def test_get_absolute_url(self):
        self.assertEqual(self.notification.get_absolute_url(),
                         '/1-test-call-for-submissions/notifications/1/')
