import os, sys, json, time, urllib, argparse, requests

def begin_capture(apikey, capture_request):
    api_endpoint = "https://api.screenshotapi.io/capture"
    print('Sending request: ' + capture_request['url'])
    capture_request['url'] = \
        urllib.pathname2url(capture_request['url']).encode('utf8')
    result = requests.post(
        api_endpoint,
        data=capture_request,
        headers={ 'apikey': apikey })
    print(result.text)
    if result.status_code == 401:
        raise Exception("Invalid API Key")
    return json.loads(result.text)['key']

def try_retrieve(apikey, key):
    api_endpoint = 'https://api.screenshotapi.io/retrieve'
    print('Trying to retrieve: ' + key)
    result = requests.get(
        api_endpoint,
        params = { 'key': key },
        headers = { 'apikey': apikey })
    json_results = json.loads(result.text)
    if json_results["status"] == "ready":
        print('Downloading image: ' + json_results["imageUrl"])
        image_result = requests.get(json_results["imageUrl"])
        return {'complete': True, 'bytes': image_result.content}
    else:
        return {'complete': False}

def get_screenshot(apikey, capture_request, save_path):
    key = begin_capture(apikey, capture_request)
    timeout_seconds = 900
    wait_seconds_counter = 0
    retry_delay_seconds = 5

    while True:
        result = try_retrieve(apikey, key)
        if result["complete"]:
            filename = os.path.join(save_path, '{}.png'.format(key))
            print("Saving screenshot to: " + key)
            open(filename, 'wb').write(result['bytes'])
            break
        else:
            wait_seconds_counter += retry_delay_seconds
            print("Screenshot not yet ready, waiting {} seconds...".format(retry_delay_seconds))
            time.sleep(retry_delay_seconds)
            if wait_seconds_counter > timeout_seconds:
                print("Timed out while attempting to retrieve: " + key)
                break
  
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--apikey', required=True, 
        help="Go to www.screenshotapi.io to get a free api key")
    parser.add_argument('--url', required=True)
    parser.add_argument('--webdriver', default="firefox",
        choices = ["firefox", "chrome", "phantomjs"])

    args = parser.parse_args()

    get_screenshot(
        apikey = args.apikey,
        capture_request = {
          'url': args.url,
          'viewport': '1200x800',
          'fullpage': False,
          'webdriver': args.webdriver,
          'javascript': True
        },
        save_path = './'
    )
