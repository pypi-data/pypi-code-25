import datetime
import pytz
from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_iasystem.exceptions import TermEvalNotCreated
from uw_iasystem.evaluation import search_evaluations,\
    get_evaluation_by_id, get_domain
from uw_iasystem.tests import fdao_ias_override


@fdao_ias_override
class IASystemTest(TestCase):

    def test_get_domain(self):
        self.assertEqual(
            get_domain("https://uw.iasystem.org/api/v1/evaluation"), "uw")
        self.assertEqual(
            get_domain("https://uw.iasysdev.org/api/v1/evaluation"), "uw")
        self.assertEqual(
            get_domain("https://uwb.iasystem.org/api/v1/evaluation"), "uwb")
        self.assertEqual(
            get_domain("https://uwt.iasystem.org/api/v1/evaluation"), "uwt")
        self.assertEqual(
            get_domain(
                "https://uweo-ap.iasystem.org/api/v1/evaluation"), "uweo-ap")
        self.assertEqual(
            get_domain(
                "https://uweo-ielp.iasystem.org/api/v1/evaluation"),
            "uweo-ielp")

    def test_search_eval(self):
        evals = search_evaluations("Seattle",
                                   year=2014,
                                   term_name='Autumn',
                                   student_id=1033334)
        self.assertEqual(evals[0].section_sln, 15314)
        self.assertTrue(evals[0].is_seattle())
        self.assertIsNotNone(evals[0].instructor_ids)
        self.assertEqual(len(evals[0].instructor_ids), 1)
        self.assertEqual(evals[0].instructor_ids[0], 851006409)
        self.assertEqual(evals[0].eval_open_date,
                         datetime.datetime(2014, 11, 24,
                                           15, 0,
                                           tzinfo=pytz.utc))
        self.assertEqual(evals[0].eval_close_date,
                         datetime.datetime(2051, 12, 3,
                                           7, 59, 59,
                                           tzinfo=pytz.utc))
        self.assertEqual(evals[0].eval_status, "Open")
        self.assertTrue(evals[0].is_open())
        self.assertEqual(evals[0].eval_url,
                         "https://uw.iasysdev.org/survey/132068")
        self.assertIsNone(evals[0].is_completed)

        self.assertEqual(evals[1].eval_status, "Closed")
        self.assertTrue(evals[1].is_closed())
        self.assertFalse(evals[1].is_completed)

        evals1 = search_evaluations("Seattle",
                                   year=2013,
                                   term_name='Spring',
                                   curriculum_abbreviation='TRAIN',
                                   course_number=100,
                                   section_id='A',
                                   student_id=1033334)
        self.assertTrue(evals1[1].is_pending())

    def test_search_report(self):
        evals = search_evaluations("seattle",
                                   year=2014,
                                   term_name='Autumn',
                                   instructor_id='123456789')
        self.assertEqual(evals[0].section_sln, 15314)
        self.assertIsNotNone(evals[0].instructor_ids)
        self.assertEqual(len(evals[0].instructor_ids), 1)
        self.assertEqual(evals[0].instructor_ids[0], 123456789)
        self.assertEqual(evals[0].report_available_date,
                         datetime.datetime(2051, 3, 1,
                                           7, 59, 59,
                                           tzinfo=pytz.utc))
        self.assertEqual(evals[0].eval_status, "Open")
        self.assertEqual(evals[0].report_url,
                         "https://uw.iasysdev.org/report/132068")
        self.assertIsNone(evals[0].is_completed)
        self.assertEqual(evals[1].eval_status, "Closed")

    def test_all_campuses(self):
        evals = search_evaluations("seattle", year=2014,
                                   term_name='Autumn', student_id=1033334)
        self.assertEqual(len(evals), 3)

        evals = search_evaluations("bothell", year=2014,
                                   term_name='Autumn', student_id=1033334)
        self.assertEqual(len(evals), 3)

        evals = search_evaluations("tacoma", year=2014,
                                   term_name='Autumn', student_id=1033334)
        self.assertEqual(len(evals), 3)

    def test_get_by_id(self):
        evals = get_evaluation_by_id(132136, "seattle")
        self.assertEqual(len(evals), 1)

    def test_multiple_instructor(self):
        evals = get_evaluation_by_id(141412, "seattle")
        self.assertEqual(len(evals), 1)
        self.assertEqual(len(evals[0].instructor_ids), 3)
        self.assertEqual(evals[0].instructor_ids[0], 849004282)
        self.assertEqual(evals[0].instructor_ids[1], 849007339)
        self.assertEqual(evals[0].instructor_ids[2], 859003192)
        self.assertEqual(evals[0].eval_open_date,
                         datetime.datetime(2015, 3, 13,
                                           14, 0,
                                           tzinfo=pytz.utc))
        self.assertEqual(evals[0].eval_close_date,
                         datetime.datetime(2015, 3, 21,
                                           6, 59, 59,
                                           tzinfo=pytz.utc))
        self.assertEqual(evals[0].eval_url,
                         "https://uw.iasystem.org/survey/141412")
        self.assertIsNone(evals[0].is_completed)

    def test_evaluation_completion(self):
        regid = "9136CCB8F66711D5BE060004AC494FFE"
        evals = search_evaluations('seattle',
                                   term_name='Spring',
                                   curriculum_abbreviation="PHYS",
                                   student_id=1033334,
                                   section_id="AQ",
                                   course_number=121,
                                   year=2013)
        self.assertEqual(evals[0].section_sln, 18545)
        self.assertIsNotNone(evals[0].instructor_ids)
        self.assertEqual(len(evals[0].instructor_ids), 1)
        self.assertEqual(evals[0].instructor_ids[0], 123456789)
        self.assertTrue(evals[0].is_completed)

        regid = "9136CCB8F66711D5BE060004AC494F31"
        evals = search_evaluations('seattle',
                                   term_name='Spring',
                                   curriculum_abbreviation="PHYS",
                                   student_id=1233334,
                                   section_id="AQ",
                                   course_number=121,
                                   year=2013)
        self.assertEqual(evals[0].section_sln, 18545)
        self.assertIsNotNone(evals[0].instructor_ids)
        self.assertEqual(len(evals[0].instructor_ids), 2)
        self.assertEqual(evals[0].instructor_ids[0], 123456789)
        self.assertEqual(evals[0].instructor_ids[1], 987654321)
        self.assertFalse(evals[0].is_completed)

    def test_multiple_evals(self):
        regid = "9136CCB8F66711D5BE060004AC494FFE"
        evals = search_evaluations('seattle',
                                   term_name='Spring',
                                   curriculum_abbreviation="TRAIN",
                                   student_id=1033334,
                                   section_id="A",
                                   course_number=100,
                                   year=2013)
        self.assertIsNotNone(evals)
        self.assertEqual(len(evals), 3)
        self.assertEqual(evals[0].section_sln, 17169)
        self.assertEqual(evals[0].eval_open_date,
                         datetime.datetime(2013, 5, 30,
                                           15, 0, 0,
                                           tzinfo=pytz.utc))
        self.assertEqual(evals[0].eval_close_date,
                         datetime.datetime(2013, 7, 1,
                                           7, 59, 59,
                                           tzinfo=pytz.utc))
        self.assertFalse(evals[0].is_completed)
        self.assertEqual(evals[1].eval_open_date,
                         datetime.datetime(2013, 6, 5,
                                           7, 0, 0,
                                           tzinfo=pytz.utc))
        self.assertEqual(evals[1].eval_close_date,
                         datetime.datetime(2013, 6, 17,
                                           6, 59, 59,
                                           tzinfo=pytz.utc))
        self.assertFalse(evals[1].is_completed)
        self.assertEqual(evals[2].eval_open_date,
                         datetime.datetime(2013, 6, 10,
                                           7, 0, 0,
                                           tzinfo=pytz.utc))
        self.assertEqual(evals[2].eval_close_date,
                         datetime.datetime(2013, 6, 19,
                                           6, 59, 59,
                                           tzinfo=pytz.utc))
        self.assertTrue(evals[2].is_completed)

    def test_search_eval_by_instructor(self):
        evals = search_evaluations("seattle",
                                   year=2014,
                                   term_name='Autumn',
                                   instructor_id=123456789)
        try:
            evals = search_evaluations("seattle",
                                       year=2015,
                                       term_name='Winter',
                                       instructor_id=123456789)
        except TermEvalNotCreated as ex:
            self.assertEqual(ex.status, 400)

        try:
            evals = search_evaluations("seattle",
                                       year=2016,
                                       term_name='Winter',
                                       instructor_id=123456789)
        except DataFailureException as ex:
            self.assertEqual(ex.status, 500)

    def test_pce_evals_by_instructor(self):
        pce_evals = search_evaluations("pce",
                                   year=2013,
                                   term_name='Summer',
                                   instructor_id=123456789)
        self.assertIsNotNone(pce_evals)
        self.assertEqual(pce_evals[0].section_sln, 165165)
        self.assertTrue(pce_evals[0].is_eo_ap())

        ap_evals = search_evaluations("pce_ap",
                                   year=2013,
                                   term_name='Summer',
                                   instructor_id=123456789)
        self.assertIsNotNone(ap_evals)
        eval0 = ap_evals[0]
        self.assertEqual(eval0.section_sln, 165165)
        self.assertTrue(eval0.is_eo_ap())
        self.assertTrue(eval0.is_online)
        self.assertFalse(eval0.is_completed)
        self.assertEqual(eval0.eval_status, "Open")
        self.assertTrue(eval0.is_open())
        self.assertEqual(eval0.response_rate, 0.0833333333333333)
        self.assertEqual(str(eval0.report_available_date),
                         '2013-09-08 07:00:00+00:00')
        self.assertEqual(str(eval0.eval_close_date),
                         '2013-08-26 06:59:59+00:00')
        self.assertEqual(str(eval0.eval_open_date),
                         '2013-08-15 07:00:00+00:00')
        self.assertEqual(eval0.eval_url,
                         "https://uweo-ap.iasystem.org/survey/19253")
        self.assertIsNone(eval0.report_url)

        ap_evals = search_evaluations("PCE_OL",
                                   year=2013,
                                   term_name='Summer',
                                   instructor_id=123456789)
        self.assertIsNotNone(ap_evals)
        self.assertEqual(ap_evals[0].section_sln, 165165)
        self.assertTrue(ap_evals[0].is_eo_ap())

        data = ap_evals[0].json_data()
        self.assertTrue(data['is_eo_ap'])

        ielp_evals = search_evaluations("PCE_IELP",
                                   year=2013,
                                   term_name='Summer',
                                   curriculum_abbreviation='CSOC',
                                   course_number=100,
                                   section_id='A',
                                   instructor_id=123456789)
        self.assertIsNotNone(ielp_evals)
        self.assertIsNotNone(str(ielp_evals[0]))
        self.assertEqual(ielp_evals[0].section_sln, 168569)
        self.assertTrue(ielp_evals[0].is_eo_ielp())
        self.assertTrue(ielp_evals[0].is_pending())

        data = ielp_evals[0].json_data()
        self.assertTrue(data['is_eo_ielp'])

        pce_evals = search_evaluations("pce",
                                   year=2013,
                                   term_name='Summer',
                                   curriculum_abbreviation='CSOC',
                                   course_number=100,
                                   section_id='A',
                                   instructor_id=123456789)
        self.assertIsNotNone(pce_evals)
        self.assertIsNotNone(str(pce_evals[0]))
        self.assertEqual(pce_evals[0].section_sln, 168569)
        self.assertTrue(pce_evals[0].is_eo_ielp())

        pce_evals = search_evaluations("pce",
                                       year=2013,
                                       term_name='Autumn',
                                       instructor_id=123456789)
        self.assertIsNone(pce_evals)
