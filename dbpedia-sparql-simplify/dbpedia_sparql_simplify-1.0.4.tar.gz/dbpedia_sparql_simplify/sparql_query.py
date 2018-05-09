# Easiest way to use this library is to instantiate an object of this class. In order to instantiate an object
# of this class, you should use sparql_util.find_resource('resource name') and use returned resource uri as
# base_resource_uri.

import dbpedia_sparql_simplify.sparql_util as util


class SparqlQuery:
    """
    'base_resource_name' can be anything you want.
    """

    def __init__(self, base_resource_name):
        base_resource_uri = util.find_resource(base_resource_name)
        if base_resource_uri is None:
            raise Exception("Given resource name is not found in database.")
        self.query = ""  # This will be the body of your SPARQL query.
        self.item_name_indicator = 0  # We use item names in SPARQL queries so we need to generate some names.
        self.resource_list = [{'label': base_resource_name, 'value': base_resource_uri, 'traceback': None}]  # We should add our base resource to our resource list, we need to use it to extend our query.
        self.select_list = []  # Select list is the list which items our query result will return.
        self.query_description = base_resource_name  # A description of this query as a human can understand.

    def find_properties(self):
        """
        Finds properties of your object.
        Ex: If your base resource is Johnny Depp and you haven't added any property to your query using
        add_property_to_query(), returns a list of properties of Johnny Depp.
        Ex2: If your base resource is Johnny Depp and you have added the partner property to your query using
        add_property_to_query(), returns a list of properties of partners of Johnny Depp.
        :rtype: list
        """
        return util.find_properties(self.resource_list)

    def add_property_to_query(self, property):
        """
        Adds a property to your query to extend your search.
        Ex: If your base resource is Johnny Depp, you can use find_properties() to get a list of properties of
        Johnny Depp. Then you can use add_property_to_query(property) to extend your search. 'property' argument here
        is a property in the list that returns from find_properties() like this:
        prop_list = my_query.find_properties()
        my_query.add_property_to_query(prop_list[5])
        """
        self.query_description = "{} of {}".format(property['label'], self.query_description)

        item_name = "?{}".format(self.query_description.replace(' ', '_'))

        self.item_name_indicator += 1
        self.query = util.query_content_add_content(self.query,
                                                    self.resource_list[-1]['value'],
                                                    property['value'],
                                                    item_name
                                                    )

        new_resource = {
            'value': item_name,
            'label': self.query_description,
            'traceback': property['value']
        }
        self.resource_list.append(new_resource)
        self.select_list.append(item_name)

    def find_objects_with_same_property(self):
        """
        If you have created a query and you want to find other objects with the same property with your query,
        you can use this function.
        Ex: Your query_description is 'partners of Johnny Depp', find_object_with_same_property will return
        other object(people) who had the same partners with Johnny Depp.
        """
        item_name = "?item_which_has_the_same_{}".format(self.query_description.replace(' ','_'))
        query = util.query_content_add_content(self.query,
                                               item_name,
                                               self.resource_list[-1]['traceback'],
                                               self.resource_list[-1]['value']
                                               )
        select_list = self.select_list[:]
        select_list.append(item_name)
        query = util.generate_query(select_list, query)
        return util.make_request(query)

    def run_query(self):
        """
        Simply runs the query that you have built and returns the results as a dictionary.
        """
        query = util.generate_query(self.select_list, self.query)
        return util.make_request(query)






