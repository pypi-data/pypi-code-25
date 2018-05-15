#############################################################
# rename or copy this file to config.py if you make changes #
#############################################################

# change this to your fully-qualified domain name to run a 
# remote server.  The default value of localhost will
# only allow connections from the same computer.
#
# for remote (cloud) deployments, it is advised to remove 
# the "local" data_sources item below, and to serve static
# files using a standard webserver
#
# if use_redis is False, server will use in-memory cache.

# TODO: Convert this to JSON file in web-accesible ('static')
# directory.  

jsonrpc_servername = "129.6.122.84"
#jsonrpc_servername = "localhost"
jsonrpc_port = 8001
http_port = 8000
serve_staticfiles = True
#use_redis = True
use_diskcache = True
diskcache_params = {"size_limit": int(0.1*2**30), "shards": 5}
use_msgpack = True
data_sources = [
    {
        "name": "ncnr_DOI",
        "DOI": "10.18434/T4201B"
    },
    {
        "name": "charlotte",        
        "url": "http://charlotte.ncnr.nist.gov/pub/",
        "start_path": ""
    },
    {
        "name": "charlotte_xray",
        "url": "http://charlotte.ncnr.nist.gov/",
        "start_path": "xraydata"
    },
    {
        "name": "ncnr",
        "url": "https://www.ncnr.nist.gov/pub/",
        "start_path": "ncnrdata"
    },
    {
        "name": "local",
        "url": "file:///"
    }
]
file_helper_url = {
    "charlotte": "http://charlotte.ncnr.nist.gov/ipeek/listftpfiles.php",
    "charlotte_xray": "http://charlotte.ncnr.nist.gov/ipeek/listhttpfiles.php",
    "ncnr": "https://www.ncnr.nist.gov/ipeek/listftpfiles.php",
    "ncnr_DOI": "https://www.ncnr.nist.gov/ipeek/listncnrdatafiles.php"
}
instruments = ["refl", "sans", "ospec"]
