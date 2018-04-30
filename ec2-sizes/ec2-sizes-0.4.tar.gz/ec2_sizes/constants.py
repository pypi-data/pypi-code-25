"""Constants"""
import os
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_INSTANCE_TYPES_FILE = os.path.join(BASE_DIR, 'ec2-sizes.pkl')
DEFAULT_REGIONS_FILE = os.path.join(BASE_DIR, 'ec2-regions.pkl')

INSTANCE_TYPE_FILE = os.environ.get('INSTANCE_TYPES_FILE',
                                    DEFAULT_INSTANCE_TYPES_FILE)
REGION_FILE = os.environ.get('REGION_FILE', DEFAULT_REGIONS_FILE)

INSTANCE_TYPES = pickle.load(open(INSTANCE_TYPE_FILE, 'rb'))
REGIONS = pickle.load(open(REGION_FILE, 'rb'))
