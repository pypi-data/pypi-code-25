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

    def __init__(self, data_type, file_path, tag, storage_key, network_key, endpoint=None):
        self.data_type = str(data_type)
        self.tag = str(tag)
        self.storage_key = str(storage_key)
        self.network_key = str(network_key)
        self.endpoint = str(endpoint) if endpoint else None
        self.file_path = str(file_path)

        self.parser = BulkXMLParser(self.file_path, self.tag, bulk_count=5000)
        self.delta = Delta()
        self.storage_manager = StorageManager(settings.STORAGE_DATABASE_URL)
        self.network_manager = NetworkManager(endpoint=self.endpoint,
                                              headers={'Authorization': 'Token cc59d524db1c5b6bb28993d5c45835bdfcf7982b'},
                                              retries=settings.NETWORK_RETRIES,
                                              timeout=90)

    def run(self):
        try:
            logger.info('xml_delta -type %r -tag %r -sk %r -nk %r -file %r -endpoint %r',
                        self.data_type, self.tag, self.storage_key, self.network_key, self.file_path, self.endpoint)

            # Clear Temp Table
            self.storage_manager.drop_listing_temp()
            self.storage_manager.create_listing_temp()

            start = time()
            for items_data in self.parser:

                temp_listings = [ListingTemp.factory(self.storage_key, self.network_key, self.data_type, item)
                                 for item in items_data]
                self.storage_manager.session.bulk_save_objects(temp_listings)
                self.storage_manager.session.commit()

            #########################################
            ############### DELETIONS ###############
            #########################################
            deleted = self.storage_manager.find_deleted(self.data_type)
            deleted_count = deleted.count()
            logger.info('%d to delete', deleted_count)

            # Perform network deletions
            if self.network_manager.enabled:
                errors = self.network_manager.bulk_delete(deleted)
                logger.info('%d errors after network deletions', len(errors.keys()))
            else:
                logger.info('No networking for deletions.')

            log(deleted, 'Deleted')
            if deleted_count > 0:
                self.storage_manager.sql_delete(self.data_type)
            logger.info('Deletions done')

            ##########################################
            ############### INSERTIONS ###############
            ##########################################
            inserted = self.storage_manager.find_inserted(self.data_type)
            inserted_count = inserted.count()
            logger.info('%d to insert', inserted_count)

            # Perform network insertions
            if self.network_manager.enabled:
                logger.info(self.endpoint)
                errors = self.network_manager.bulk_post(inserted)
                logger.info('%d errors after network insertions', len(errors.keys()))
            else:
                logger.info('No networking for insertions.')

            log(inserted, 'Inserted')
            if inserted_count > 0:
                self.storage_manager.sql_insert(self.data_type)
            logger.info('Insertions done')

            #######################################
            ############### UPDATES ###############
            #######################################
            updated = self.storage_manager.find_updated(self.data_type)
            updated_count = updated.count()
            logger.info('%d to update', updated_count)

            # Perform network updates
            if self.network_manager.enabled:
                errors = self.network_manager.bulk_post(updated)
                logger.info('%d errors after network updates', len(errors.keys()))
            else:
                logger.info('No networking for updates.')

            log(updated, 'Updated')
            if updated_count > 0:
                self.storage_manager.sql_update(self.data_type)
            logger.info('Updates done')

            logger.info(('Finished delta\n'
                         '\tType: %r\n'
                         '\tTag: %r\n'
                         '\tStorage Key: %r\n'
                         '\tNetwork Key: %r\n'
                         '\tFile: %r\n'
                         '\tEndpoint: %r\n'
                         '\tTime elapsed: %s'),
                        self.data_type, self.tag, self.storage_key, self.network_key, self.file_path, self.endpoint,
                        timedelta(seconds=time()-start))
        except Exception:
            logger.exception('Delta task %r - %r - %r - %r - %r - %r',
                             self.data_type, self.tag, self.storage_key, self.network_key, self.file_path, self.endpoint)
