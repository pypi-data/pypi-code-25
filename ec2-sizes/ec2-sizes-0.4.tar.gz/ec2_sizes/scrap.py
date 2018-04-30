import pickle
import json
from collections import defaultdict
import requests
import ijson

FILEPATH = '/tmp/ec.json'
URL = "https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonEC2/current/index.json"
IGNORED_FIELDS = ['locationType', 'operatingSystem']


def download_json():
    response = requests.get(URL, stream=True)
    with open(FILEPATH, 'wb') as fo:
        for chunk in response.iter_content(chunk_size=2**20):
            if chunk:
                fo.write(chunk)
    return open(FILEPATH, 'r')


def get_json():
    try:
        return open(FILEPATH, 'r')
    except IOError:
        return download_json()


def parse():
    json_file = get_json()
    flavors = {}
    regions = defaultdict(list)
    products_data = ijson.items(json_file, 'products')
    products_data = next(products_data)
    for sku in products_data:
        if products_data[sku]['productFamily'] != "Compute Instance":
            continue
        location = products_data[sku]['attributes']['location']
        instance_type = products_data[sku]['attributes']['instanceType']
        regions[location].append(instance_type)
        if instance_type not in flavors:
            for field in IGNORED_FIELDS:
                products_data[sku]['attributes'].pop(field, None)
            flavors[instance_type] = products_data[sku]['attributes']
    return flavors, regions


def dump():
    flavors, regions = parse()
    flavors, regions = json.dumps(flavors), json.dumps(regions)
    with open('ec2-sizes.json', 'w') as fd:
        fd.write(flavors)
    with open('ec2-sizes.pkl', 'wb') as fd:
        pickle.dump(flavors, fd, protocol=2)
    with open('ec2-regions.json', 'w') as fd:
        fd.write(regions)
    with open('ec2-regions.pkl', 'wb') as fd:
        pickle.dump(regions, fd, protocol=2)


if __name__ == '__main__':
    dump()
