# -*- coding: utf-8 -*-

"""Main module."""
from datetime import timedelta
from time import time, strftime
import logging

from . import settings

from .bulk_xml_parser import BulkXMLParser
from .delta import Delta
from .models import Listing, ListingTemp, NetworkError
from .storage_manager import StorageManager
from .network_manager import NetworkManager
from .utils import log


logger = logging.getLogger(__name__)


class DeltaTask(object):

    total_parsed = 0
    total_changed = 0

    def __init__(self, data_type, file_path, tag, pk, endpoint=None):
        self.data_type = str(data_type)
        self.tag = str(tag)
        self.pk = str(pk)
        self.endpoint = str(endpoint) if endpoint else None
        self.file_path = str(file_path)

        self.parser = BulkXMLParser(self.file_path, self.tag, bulk_count=5000)
        self.delta = Delta()
        self.storage_manager = StorageManager(settings.STORAGE_DATABASE_URL)
        self.network_manager = NetworkManager(endpoint=self.endpoint,
                                              headers=None,
                                              retries=settings.NETWORK_RETRIES,
                                              timeout=90)

    def run(self):
        try:
            logger.info('xml_delta -type %r -tag %r -pk %r -file %r -endpoint %r',
                        self.data_type, self.tag, self.pk, self.file_path, self.endpoint)

            # Clear Temp Table
            self.storage_manager.drop_listing_temp()
            self.storage_manager.create_listing_temp()

            start = time()
            for items_data in self.parser:

                temp_listings = [ListingTemp.factory(self.pk, self.data_type, item)
                                 for item in items_data]
                self.storage_manager.session.bulk_save_objects(temp_listings)
                self.storage_manager.session.commit()

            deleted = self.storage_manager.find_deleted(self.data_type)
            logger.info('%d to delete', deleted.count())

            # Perform network deletions
            if self.network_manager.enabled:
                errors = self.network_manager.bulk_delete(deleted)
                logger.info('%d errors after network deletions', len(errors.keys()))
            else:
                logger.info('No networking for deletions.')

            log(deleted, 'Deleted')
            self.storage_manager.sql_delete()
            logger.info('Deletions done')

            inserted = self.storage_manager.find_inserted(self.data_type)
            logger.info('%d to insert', inserted.count())

            # Perform network insertions
            if self.network_manager.enabled:
                logger.info(self.endpoint)
                errors = self.network_manager.bulk_post(inserted)
                logger.info('%d errors after network insertions', len(errors.keys()))
            else:
                logger.info('No networking for insertions.')

            log(inserted, 'Inserted')
            self.storage_manager.sql_insert()
            logger.info('Insertions done')

            updated = self.storage_manager.find_updated(self.data_type)
            logger.info('%d to update', updated.count())

            # Perform network updates
            if self.network_manager.enabled:
                errors = self.network_manager.bulk_post(updated)
                logger.info('%d errors after network updates', len(errors.keys()))
            else:
                logger.info('No networking for updates.')

            log(updated, 'Updated')
            self.storage_manager.sql_update(self.data_type)
            logger.info('Updates done')

            logger.info(('Finished delta\n'
                         '\tType: %r\n'
                         '\tTag: %r\n'
                         '\tKey: %r\n'
                         '\tFile: %r\n'
                         '\tEndpoint: %r\n'
                         '\tTime elapsed: %s'),
                        self.data_type, self.tag, self.pk, self.file_path, self.endpoint,
                        timedelta(seconds=time()-start))
        except Exception:
            logger.exception('Delta task %r - %r - %r - %r - %r',
                             self.data_type, self.tag, self.pk, self.file_path, self.endpoint)
