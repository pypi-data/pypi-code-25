import dpostools.legacy as legacy
from unittest import TestCase
import pprint


class TestLegace(TestCase):
    def test_get_events(self):
        legacy.set_connection(
            host="localhost",
            database="ark_mainnet",
            user="karel",
            password="Dwl1ml12_3#"
        )

        legacy.set_delegate(
            address="AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE",
            pubkey="0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a",
        )

        res = legacy.get_events("0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a")
        self.assertTrue(len(res) > 100)

    # def test_trueshare_ark(self):
    #     legacy.set_connection(
    #         host="localhost",
    #         database="ark_mainnet",
    #         user="karel",
    #         password="Dwl1ml12_3#"
    #     )
    #
    #     legacy.set_delegate(
    #         address="AZse3vk8s3QEX1bqijFb21aSBeoF6vqLYE",
    #         pubkey="0218b77efb312810c9a549e2cc658330fcc07f554d465673e08fa304fa59e67a0a",
    #     )
    #
    #     true = legacy.Delegate.trueshare()[0]
    #     dep = legacy.Delegate.dep_trueshare()[0]
    #
    #     self.assertEqual(len(true), len(dep))
    #
    #     for i in true:
    #         if dep[i]["share"] != 0:
    #            self.assertTrue(0.95 < true[i]["share"]/dep[i]["share"] < 1.1)
    #         else:
    #             self.assertTrue(true[i]["share"] == 0)

    # def test_trueshare_kapu(self):
    #     legacy.set_connection(
    #         host="localhost",
    #         database="kapu_mainnet",
    #         user="karel",
    #         password="Dwl1ml12_3#"
    #     )
    #
    #     legacy.set_delegate(
    #         address="KCVZBoRwmUc3U6c5ZhqmDokzNuhmbUAt6f",
    #         pubkey="03b0dd2650100ac70f4b4b0d6f83c5f17e197c47a975c6c807013edbba88cd7efa",
    #     )
    #
    #     true = legacy.Delegate.trueshare()[0]
    #     dep = legacy.Delegate.dep_trueshare(raiseError=False)[0]
    #
    #     print(len(true))
    #     print(len(dep))
    #     self.assertEqual(len(true), len(dep))
    #
    #     for i in true:
    #         if dep[i]["share"] != 0:
    #            print(true[i]["share"]/dep[i]["share"])
    #            self.assertTrue(0.95 < true[i]["share"]/dep[i]["share"] < 1.1)
    #         else:
    #             self.assertTrue(true[i]["share"] == 0)
