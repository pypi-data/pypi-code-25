#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
Created by Marsel Tzatzo on 05/12/2017.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Listing, ListingTemp, NetworkError

class StorageManager(object):

    def __init__(self, connection_string):
        super(StorageManager, self).__init__()
        self.connection_string = connection_string
        self.engine = create_engine(self.connection_string)
        self.session_maker_factory = sessionmaker(bind=self.engine)
        self.session = self.session_maker_factory()
        Base.metadata.create_all(self.engine)

    #region Listing

    def fetch_listings(self, data_type, ids):
        return self.session.query(Listing).filter(Listing.storage_key.in_(ids),
                                                  Listing.type == data_type).all()

    def delete_listings(self, ids=None, type=None):
        """
        Removes all listings with the given type if type is not null.

        :param type:
        :return:
        """
        filters = []
        if type:
            filters.append(Listing.type == type)
        if ids:
            filters.append(Listing.storage_key.in_(ids))
        self.session.query(Listing).filter(*filters).delete(synchronize_session=False)
        self.session.commit()

    def insert_listings(self, listings):
        self.session.bulk_save_objects(listings)
        self.session.commit()

    def update_listings(self, listings):
        for listing in listings:
            self.session.merge(listing)
        self.session.commit()

    def count_type(self, type):
        return (self.session
                .query(Listing)
                .filter(Listing.type == type)
                .count())

    def find_inserted(self, type):
        return self.session.query(ListingTemp)\
            .filter(~ListingTemp.storage_key.in_(self.session.query(Listing)
                                                 .filter(Listing.type == type)
                                                 .with_entities(Listing.storage_key)))

    def find_updated(self, type):
        return self.session.query(ListingTemp)\
            .join(Listing, ListingTemp.storage_key == Listing.storage_key)\
            .filter(Listing.type == type,
                    Listing.data != ListingTemp.data)

    def find_deleted(self, type):
        return self.session.query(Listing).filter(Listing.type == type,
                                 ~Listing.storage_key.in_(self.session.query(ListingTemp)
                                                          .with_entities(ListingTemp.storage_key)))

    def sql_update(self, type):
        self.session.execute("""UPDATE listing 
                                    JOIN listingtemp on listing.storage_key = listingtemp.storage_key 
                                SET listing.data = listingtemp.data, listing.updated = NOW() 
                                WHERE listing.type = '{0}' AND listing.data <> listingtemp.data;""".format(type))
        self.session.commit()

    def sql_delete(self, type):
        self.session.execute("""DELETE FROM listing WHERE type = '{0}' and  storage_key not in 
                                (SELECT storage_key from listingtemp);""".format(type))
        self.session.commit()

    def sql_insert(self, type):
        self.session.execute("""INSERT INTO listing (storage_key, type, network_key, data, sent, created, updated) 
                                SELECT * from listingtemp WHERE storage_key not in 
                                (SELECT storage_key from listing where listing.type = '{0}');""".format(type))
        self.session.commit()

    def drop_all(self):
        Listing.__table__.drop(self.engine)
        ListingTemp.__table__.drop(self.engine)
        NetworkError.__table__.drop(self.engine)

    def drop_listing_temp(self):
        ListingTemp.__table__.drop(self.engine)
        self.session.commit()

    def create_listing_temp(self):
        ListingTemp.__table__.create(self.engine)
        self.session.commit()

    #end region

    #region Network Error

    def insert_network_errors(self, network_errors):
        self.session.bulk_save_objects(network_errors)
        self.session.commit()

    def get_network_errors(self):
        return self.session.query(NetworkError)

    def clear_network_errors(self):
        self.session.query(NetworkError).delete()
        self.session.commit()

    #endregion
