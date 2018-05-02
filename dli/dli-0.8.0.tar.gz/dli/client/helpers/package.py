
def get_datasets(package):
    datasets = list(package.package_datasets().get_entities('dataset'))
    return datasets
