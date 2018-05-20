from submitify.tests import (
    TestCase,

    # CallMixin,
    # GuidelineMixin,
    # NotificationMixin,
    # ReviewMixin,
    # SubmissionMixin,
    # UserMixin,
)


class TestCreateReview(TestCase):
    def test_owner_or_readers_only(self):
        pass

    def test_submission_advanced(self):
        # advanced to in_review at first review, advanced to reviewed when
        # quota is met
        pass

    def test_review_created(self):
        pass


class TestViewReview(TestCase):
    def test_owner_or_readers_only_shortcut(self):
        pass

    def test_reviewer_or_call_owner_only(self):
        pass

    def test_renders(self):
        pass


class TestEditReview(TestCase):
    def test_review_owner_only(self):
        pass

    def test_review_updated(self):
        pass
