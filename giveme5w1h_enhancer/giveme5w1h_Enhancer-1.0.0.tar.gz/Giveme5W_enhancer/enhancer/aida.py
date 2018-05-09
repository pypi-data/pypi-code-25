import requests
import datetime
import time
from .abs_enhancer import AbsEnhancer

class Aida(AbsEnhancer):
    """
      default service is calling  https://www.ambiverse.com/pricing/
      at the time of writing there is a request limit 60 API calls per minute/1K API calls per month
      setup your own server for request
    """
    def __init__(self, questions, url=None):
        super().__init__(questions)
        self._last_request = None
        if not url:
            self._url = 'https://gate.d5.mpi-inf.mpg.de/aida/service/disambiguate'
            self._limit_request_rate = True
        else:
            self._url = url

    def get_enhancer_id(self):
        return 'aida'

    def process(self, document):
        # make sure there is just one call per second, if rate is limited
        if self._limit_request_rate:
            # AIDA-Service is very sensitive to multiple requests and request frequency
            # this 10 seconds of sleep make sure it goes well
            # this limits the rate to 8640 request per day
            time.sleep(10)

        with requests.Session() as s:
            r = s.post(self._url, stream=False, data={'text': document.get_full_text()},  headers={'Connection':'close'})
            if self._limit_request_rate:
                self._last_request = datetime.datetime.now()
            if r.status_code == 200:
                o = r.json()
            else:
                print(r.content)
            r.close()
            document.set_enhancement(self.get_enhancer_id(), o)

    def process_data(self, process_data, character_offset):
        # there could be more than one mention per character_offset
        result = []
        for mention in process_data['mentions']:
            offset = mention['offset']
            length = mention['length']

            process_data_offset = (offset, offset+length)

            if self.is_overlapping(character_offset, process_data_offset):
                bestEntity = mention.get('bestEntity')
                bestEntityMetadata = None

                # some have no Entity in the dataset
                if bestEntity:
                    bestEntityMetadata = process_data['entityMetadata'][bestEntity['kbIdentifier']]

                # TODO: besides bestEntityMetadata there are more under all (sometimes)
                result.append({'mention': mention, 'bestEntityMetadata': bestEntityMetadata})
        return result

