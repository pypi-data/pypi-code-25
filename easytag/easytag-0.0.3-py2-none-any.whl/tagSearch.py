import argparse
import io
from google.cloud import vision

def get_tags(request):
    """
    get_tags takes a request as a parameter and returns a string of tags separated by commas
    """
    client = vision.ImageAnnotatorClient()

    result = client.annotate_image(request)
    labels = result.label_annotations
    output = ''

    if labels:
        for label in labels:
            output += label.description + ','
        output = output[:-1]
    else:
        output = "no tags found"
        
    return output

def main():
    """
    main parses command-line arguments into a request, passes the request to get_tags, and prints the result
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", help="get tags based on image URL rather than local file", action="store_true")
    parser.add_argument("target", help="file or URL to get tags for", type=str)
    args = parser.parse_args()

    if args.url:
        request = {
            'image': {
                'source': {
                    'image_uri': args.target
                },
            },
            "features": [
                {
                    "type": "LABEL_DETECTION",
                }
            ],
        }
    else:
        with io.open(args.target, 'rb') as image_file:
            content = image_file.read()

        request = {
            "image": {
                "content": content
            },
            "features": [
                {
                    "type": "LABEL_DETECTION",
                }
            ],
        }

    result = get_tags(request)
    print(result)

    return(0)