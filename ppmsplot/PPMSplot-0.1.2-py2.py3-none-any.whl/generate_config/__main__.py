import json
import os


def main():
    dir_path = os.getcwd()
    fp = os.path.join(dir_path, 'config.json')
    print(fp)
    with open(fp, 'w') as config_file:
        json.dump(
            {
                "plotSettings":{
                    "outputFilename":"example.png",
                    "figureTitle":"Figure title",
                    "xTitle":"x axis",
                    "yTitle":"y axis",
                    "legend":True,
                    "flipX": False,
                    "flipY": False,
                    "xMin":0,
                    "xMax":100,
                    "yMin":0,
                    "yMax":100,
                    "grid":False
                },
                "files":[
                    {
                        "filename":"example.dat",
                        "rowStart":36,
                        "rowEnd":0,
                        "series":[
                            {
                                "label":"example",
                                "style":"-",
                                "xColumnIndex":2,
                                "yColumnIndex":4,
                                "xMin":0,
                                "xMax":3200
                            }
                        ]
                    }
                ]
            },
            config_file,
            indent=4
        )

if __name__ == "__main__":
    main()