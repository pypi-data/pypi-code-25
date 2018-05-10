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
        return self.session.query(Listing).filter(Listing.dasUniqueId.in_(ids),
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
            filters.append(Listing.dasUniqueId.in_(ids))
        self.session.query(Listing).filter(*filters).delete(synchronize_session=False)
        self.session.commit()

    def insert_listings(self, listings):
        self.session.bulk_save_objects(listings)
        self.session.commit()

    def update_listings(self, listings):
        for listing in listings:
            self.session.merge(listing)
        self.session.commit()

    def find_inserted(self, type):
        return self.session.query(ListingTemp)\
            .filter(~ListingTemp.dasUniqueId.in_(self.session.query(Listing)
                                                 .filter(Listing.type == type)
                                                 .with_entities(Listing.dasUniqueId)))

    def find_updated(self, type):
        return self.session.query(Listing)\
            .join(ListingTemp, Listing.dasUniqueId == ListingTemp.dasUniqueId)\
            .filter(Listing.type == type,
                    Listing.data != ListingTemp.data)

    def find_deleted(self, type):
        return self.session.query(Listing).filter(Listing.type == type,
                                 ~Listing.dasUniqueId.in_(self.session.query(ListingTemp)
                                                          .with_entities(ListingTemp.dasUniqueId)))

    def sql_update(self, type):
        self.session.execute("""UPDATE listing 
                                    JOIN listingtemp on listing.dasUniqueId = listingtemp.dasUniqueId 
                                SET listing.data = listingtemp.data, listing.updated = NOW() 
                                WHERE listing.type = '{0}' AND listing.data <> listingtemp.data;""".format(type))
        self.session.commit()

    def sql_delete(self):
        self.session.execute("""DELETE FROM listing WHERE dasUniqueId not in (SELECT dasUniqueId from listingtemp);""")
        self.session.commit()

    def sql_insert(self):
        self.session.execute("""INSERT INTO listing (dasUniqueId, type, data, sent, created, updated) 
                                SELECT * from listingtemp WHERE dasUniqueId not in (SELECT dasUniqueId from listing);""")
        self.session.commit()

    def drop_all(self):
        Listing.__table__.drop(self.engine)
        ListingTemp.__table__.drop(self.engine)
        NetworkError.__table__.drop(self.engine)

    def drop_listing_temp(self):
        ListingTemp.__table__.drop(self.engine)
        self.session.commit()

    def create_listing_temp(self):
        Base.metadata.create_all(self.engine)

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
