from opendns import InvestigateApi

if __name__ == "__main__":
    inv = InvestigateApi('5bbd4ecf-3cfd-4a0e-a9da-1e61f8cdfd3a')
    pattern = '.*yelp.*'
    import pdb; pdb.set_trace()
    patterns = [pattern]
    results = inv.search(patterns)
    print(results)
