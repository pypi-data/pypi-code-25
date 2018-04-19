import argparse
import io
from google.cloud import vision

def get_tags(request):
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