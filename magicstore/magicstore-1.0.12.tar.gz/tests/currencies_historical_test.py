from magicstore import mongo


def test_should_return_all_global_statistics():
    # set mongo uri in system variables
    for document in mongo.currencies_historical().bitcoin():
        print(document)
