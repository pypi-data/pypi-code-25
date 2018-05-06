
import logging
lgr = logging.getLogger('datalad.magic')

import time

lgr.info('MESSAGE', extra=dict(dlm_progress='mickey', dlm_progress_total=3))
lgr.info('MESSAGE', extra=dict(dlm_progress='mickey', dlm_progress_update=1, dlm_progress_increment=True))
time.sleep(1)
lgr.info('MESSAGE', extra=dict(dlm_progress='mickey', dlm_progress_update=1, dlm_progress_increment=True))
time.sleep(1)
lgr.info('MESSAGE', extra=dict(dlm_progress='mickey', dlm_progress_update=1, dlm_progress_increment=True))
time.sleep(1)
lgr.info('MESSAGE', extra=dict(dlm_progress='mickey'))
