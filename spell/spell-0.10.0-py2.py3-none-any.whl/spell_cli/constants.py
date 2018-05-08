BLACKLISTED_FILES = {
    ".DS_Store"
}

DEFAULT_SUPPORTED_OPTIONS = {
    "frameworks": {
        "values": [
            "caffe",
            "caffe2",
            "mxnet",
            "pytorch",
            "tensorflow",
        ],
    },
    "machine_types": {
        "values": [
            "CPU",
            "K80",
            "V100",
        ],
        "default": "CPU",
    },
}
