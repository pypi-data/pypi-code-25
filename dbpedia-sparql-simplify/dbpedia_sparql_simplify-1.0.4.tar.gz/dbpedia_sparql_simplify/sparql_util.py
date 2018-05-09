import requests
import dbpedia_sparql_simplify.sparql_query
import unicodecsv as csv

url_start = "http://dbpedia.org/sparql?" \
            "default-graph-uri=http%3A%2F%2Fdbpedia.org" \
            "&query=" \
            "PREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0A"

url_end = "&output=json"


def generate_url(query):
    return url_start + query + url_end


def generate_query(select_list, query_content):
    select = ""
    for item in select_list:
        select += item + " "
    return "SELECT DISTINCT " + select + " WHERE{" + query_content + "}"


def query_content_add_content(query_content, arg1, arg2, arg3):
    query_content += '{} {} {}.'.format(arg1, arg2, arg3)
    return query_content


def make_request(query):
    url = generate_url(query)
    r = requests.get(url)

    if r.status_code != 200:
        return
    result_raw = r.json()
    if result_raw['results']['bindings'] is None:
        return

    result = []
    for key in result_raw['results']['bindings']:
        result.append(key)

    return result


def find_resource(name):
    query = "SELECT DISTINCT * " \
            "WHERE{" \
            "?item rdfs:label ?itemLabel." \
            "FILTER (?itemLabel = '" + name + "'@en ). " \
                                              "}"
    results = make_request(query)
    if len(results) == 0:
        return

    resource = None
    for result in results:
        if '/resource/' in result['item']['value']:
            resource = result['item']['value']
            break

    if resource is None:
        resource = results[0]['item']['value']

    return "<{}>".format(resource)


def find_properties(resource_list):
    s = ""
    for i in range(len(resource_list)):
        if i > 0:
            s += "{} {} {}.".format(resource_list[i - 1]['value'], resource_list[i]['traceback'], resource_list[i]['value'])

    s += resource_list[-1:][0]['value']
    query = "SELECT DISTINCT ?property ?propertyLabel " \
            "WHERE{" \
            "" + s + " ?property ?value." \
                     "?property rdfs:label ?propertyLabel." \
                     "FILTER (lang(?propertyLabel) = 'en')" \
                     "}"
    result = make_request(query)
    if result is None:
        return

    properties = []
    for binding in result:
        property = {'label': binding['propertyLabel']['value'], 'value': "<{}>".format(binding['property']['value'])}
        properties.append(property)

    return properties



