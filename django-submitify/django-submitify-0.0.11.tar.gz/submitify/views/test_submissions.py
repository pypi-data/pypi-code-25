from submitify.tests import (
    TestCase,

    # CallMixin,
    # GuidelineMixin,
    # NotificationMixin,
    # ReviewMixin,
    # SubmissionMixin,
    # UserMixin,
)


class TestManuscriptify(TestCase):
    def test_all_steps(self):
        # TODO move to models
        pass


class TestCreateSubmission(TestCase):
    def test_call_not_open(self):
        pass

    def test_call_invite_only(self):
        pass

    def test_call_readers_cant_submit(self):
        pass

    def test_submission_created(self):
        # TODO stub manuscriptify
        pass


class TestViewSubmission(TestCase):
    def test_owner_or_readers_only(self):
        pass

    def test_can_review_for_call_status(self):
        pass

    def test_can_review_for_submission_status(self):
        pass

    def test_creates_review(self):
        pass

    def test_updates_review(self):
        pass

    def test_renders(self):
        pass


class TestViewSubmissionText(TestCase):
    def test_owner_or_readers_only(self):
        pass

    def test_renders(self):
        pass


class TestViewSubmissionFile(TestCase):
    def test_owner_or_readers_only(self):
        pass

    def test_renders(self):
        pass


class TestViewOriginalFile(TestCase):
    def test_owner_or_readers_only(self):
        pass

    def test_renders(self):
        pass


class TestResolveSubmission(TestCase):
    def test_owner_only(self):
        pass

    def test_resolve_only_during_review_phase(self):
        pass

    def test_resolves(self):
        pass
