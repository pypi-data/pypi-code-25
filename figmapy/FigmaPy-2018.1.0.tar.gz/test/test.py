from FigmaPy.figmapy import FigmaPy as Figma
import json
import os

print(os.getcwd())


class ImageID:
    def __init__(self, name, id):
        self.name = name
        self.id = id


def main():
    file_key = 'IHz6rmmsikrf0llG98m1W3ry'
    f = Figma('1201-32c89e9e-e11a-47bc-8f37-f3ef192b3759')
    file_data = f.get_file(file_key)

    image_ids = []
    for x in file_data.document['children']:
        for y in x['children']:
            if y['type'] == 'FRAME':
                image_ids.append(y['id'])

    images = f.get_file_images(file_key, image_ids)
    for key in images.images:
        print(images.images[key])


if __name__ == '__main__':
    main()
