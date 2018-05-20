from submitify.tests import (
    TestCase,

    # CallMixin,
    # GuidelineMixin,
    # NotificationMixin,
    # ReviewMixin,
    # SubmissionMixin,
    # UserMixin,
)


class TestListCalls(TestCase):
    def test_lists_open_calls(self):
        self.assertTrue(True)

    def test_lists_other_calls_if_asked(self):
        pass


class TestViewCall(TestCase):
    def test_view_call(self):
        pass

    def test_lists_notifications(self):
        pass

    def test_can_submit_call_open_only(self):
        pass

    def test_can_submit_invite_only(self):
        pass

    def test_can_submit_if_reader(self):
        pass


class TestCreateCall(TestCase):
    def test_form_renders(self):
        pass

    def test_form_saves(self):
        pass

    def test_guidelines_save(self):
        pass


class TestEditCall(TestCase):
    def test_owner_only(self):
        pass

    def test_form_renders(self):
        pass

    def test_form_saves(self):
        pass

    def test_guidelines_save(self):
        pass


class TestInviteReader(TestCase):
    def test_reader_invited(self):
        pass

    def test_cant_invite_owner(self):
        pass


class TestInviteWriter(TestCase):
    def test_writer_invited(self):
        pass

    def test_cant_invite_owner(self):
        pass

    def test_cant_invite_unless_invite_only(self):
        pass


class TestNextStep(TestCase):
    def test_owner_only(self):
        pass

    def test_call_advanced(self):
        pass

    def test_cant_proceed_beyond_max(self):
        pass

    def test_cant_proceed_to_finished_with_unreviewed_submissions(test):
        pass

    def test_moves_submissions_to_review_if_closing(test):
        pass
